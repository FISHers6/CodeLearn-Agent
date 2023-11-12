mod chain;
mod handler;
mod middleware;
mod request;
mod response;
mod router;
mod body;
mod errors;

use crate::chain::Chain;
use crate::handler::Handler;
use crate::middleware::Middleware;
use crate::request::Request;
use crate::response::Response;
use crate::router::Router;
use futures_util::{future, TryFutureExt};
use hyper::service::Service;
use hyper::Error;
use hyper::Server;
use route_recognizer::Match;
use std::future::Future;
use std::net::{SocketAddr, ToSocketAddrs};
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll};

pub type Result<T = Response> = std::result::Result<T, Error>;

pub struct App<State> {
    state: State,
    router: Arc<Router<State>>,
    middlewares: Arc<Vec<Arc<dyn Middleware<State>>>>,
}

impl App<()> {
    fn new() -> Self {
        Self::build(())
    }
}

impl<State> App<State>
where
    State: Clone + Send + Sync + 'static,
{
    pub fn build(state: State) -> Self {
        App {
            state,
            router: Arc::new(Router::new()),
            middlewares: Arc::new(vec![]),
        }
    }

    pub fn with<M: Middleware<State>>(&mut self, middleware: M) -> &mut Self {
        let middlewares = Arc::get_mut(&mut self.middlewares).expect("Can not find middlewares");
        middlewares.push(Arc::new(middleware));
        self
    }

    pub fn get<S: AsRef<str>, F: Handler<State>>(mut self, path: S, handler: F) -> App<State> {
        let router = Arc::get_mut(&mut self.router).expect("Can not find router");
        let _ = router.get(path, handler);
        self
    }

    pub fn post<S: AsRef<str>, F: Handler<State>>(mut self, path: S, handler: F) -> App<State> {
        let router = Arc::get_mut(&mut self.router).expect("Can not find router");
        let _ = router.post(path, handler);
        self
    }

    pub fn put<S: AsRef<str>, F: Handler<State>>(mut self, path: S, handler: F) -> App<State> {
        let router = Arc::get_mut(&mut self.router).expect("Can not find router");
        let _ = router.post(path, handler);
        self
    }

    pub async fn swim<A>(&self, addr: A)
    where
        A: ToSocketAddrs,
    {
        let addr: SocketAddr = addr.to_socket_addrs().unwrap().next().unwrap();
        let server = Server::bind(&addr)
            .serve(MakeService(self.clone()))
            .map_err(|e| println!("server error: {}", e));
        let _ = server.await;
    }
}

impl<State: Clone> Clone for App<State> {
    fn clone(&self) -> Self {
        Self {
            state: self.state.clone(),
            router: self.router.clone(),
            middlewares: self.middlewares.clone(),
        }
    }
}

impl<State: Clone + Send + Sync + 'static> Service<hyper::Request<hyper::body::Body>>
    for App<State>
{
    type Response = hyper::Response<hyper::body::Body>;
    type Error = Error;
    type Future =
        Pin<Box<dyn Future<Output = std::result::Result<Self::Response, Self::Error>> + Send>>;

    fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<std::result::Result<(), Self::Error>> {
        Ok(()).into()
    }

    fn call(&mut self, req: hyper::Request<hyper::body::Body>) -> Self::Future {
        let Self {
            state,
            router,
            middlewares,
        } = self.clone();
        println!("call app");
        let future = async move {
            // 取出路由
            let method = req.method().to_owned();
            let path = req.uri().path();
            println!("path: {}", path);
            let mut response = Response::new();
            if let Some(Match { handler, params }) = router.find(path, &method) {
                let request: Request<State> =
                    Request::from_http(req, state, params);
                // 取出下一个执行的中间件并链式执行
                let chain = Chain {
                    handler,
                    next: &middlewares,
                };
                response = chain.call(request).await;
            } else {
                response.set_status(404)
            }
            Ok(response.into())
        };
        Box::pin(future)
    }
}

/// MakeService实现了Service trait
/// 并且满足了MakeServiceRef trait的要求: S满足HttpService
/// 所以满足MakeServiceRef<I::Conn, Body, ResBody = B>
pub struct MakeService<State>(App<State>);

impl<T, State: Clone> Service<T> for MakeService<State> {
    type Response = App<State>;
    type Error = std::io::Error;
    type Future = future::Ready<std::result::Result<Self::Response, Self::Error>>;

    fn poll_ready(&mut self, _cx: &mut Context<'_>) -> Poll<std::result::Result<(), Self::Error>> {
        Ok(()).into()
    }

    fn call(&mut self, _: T) -> Self::Future {
        println!("call make service");
        future::ok(self.0.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::App;
    use crate::chain::Chain;
    use crate::middleware::Middleware;
    use crate::request::Request;
    use crate::response::Response;
    use async_trait::async_trait;
    use std::future::Future;
    use std::pin::Pin;
    use http::StatusCode;
    use serde_derive::{Deserialize, Serialize};

    fn after<'a>(
        request: Request<()>,
        chain: Chain<'a, ()>,
    ) -> Pin<Box<dyn Future<Output = crate::Result> + 'a + Send>> {
        let future = async move {
            let response = chain.call(request).await;
            println!("after middleware");
            Ok(response)
        };
        Box::pin(future)
    }

    struct Before<F>(pub F);

    #[async_trait]
    impl<State, F, Fut> Middleware<State> for Before<F>
    where
        State: Clone + Send + Sync + 'static,
        F: Fn(Request<State>) -> Fut + Send + Sync + 'static, // acquire a request
        Fut: Future<Output = Request<State>> + Send + Sync + 'static, // return a new request
    {
        async fn handle(&self, request: Request<State>, chain: Chain<'_, State>) -> crate::Result {
            let request = (self.0)(request).await;
            Ok(chain.call(request).await)
        }
    }

    #[tokio::test]
    async fn example() {
        let _app = App::new()
            .get("/hello", |request: Request<_>| async move {
                println!("request: {}", request.url());
                println!("params: {:?}", request.params());
                println!("headers: {:?}", request.headers());
                Ok(Response::new())
            })
            .get("/world", |request: Request<_>| async move {
                println!("request: {}", request.url());
                Ok(Response::new())
            })
            .with(Before(|request: Request<_>| async move {
                println!("before middleware, request.url: {}", request.url());
                request
            }))
            .with(after)
            .swim("127.0.0.1:8008")
            .await;
    }

    #[derive(Deserialize, Debug)]
    struct Todo {
        id: i64,
        title: String,
        description: String,
    }

    #[tokio::test]
    async fn json_body() {
        let _app = App::new()
            .post("/body", |mut request: Request<_>| async move {
                let mut response = Response::new();
                let todo: anyhow::Result<Todo> = request.parse_json().await;
                match todo {
                    Ok(todo) => {
                        println!("{:#?}", todo);
                        // todo Response结构实现写数据
                        Ok(response)
                    }
                    Err(err) => {
                        response.set_status(StatusCode::BAD_REQUEST);
                        Ok(response)
                    }
                }
            })
            .swim("127.0.0.1:8009")
            .await;
    }
}
