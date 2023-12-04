use crate::request::Request;
use crate::response::Response;
use async_trait::async_trait;
use std::future::Future;

#[async_trait]
pub trait Handler<State: Clone + Send + Sync + 'static>: Send + Sync + 'static {
    async fn call(&self, request: Request<State>) -> crate::Result;
}

#[async_trait]
impl<State, F, Fut, Res> Handler<State> for F
where
    State: Clone + Send + Sync + 'static,
    F: Send + Sync + 'static + Fn(Request<State>) -> Fut,
    Fut: Future<Output = Result<Res, hyper::Error>> + Send + 'static,
    Res: Into<Response> + 'static,
{
    async fn call(&self, request: Request<State>) -> crate::Result {
        let future = (self)(request);
        let response = future.await?;
        Ok(response.into())
    }
}

#[async_trait]
impl<State: Clone + Send + Sync + 'static> Handler<State> for Box<dyn Handler<State>> {
    async fn call(&self, request: Request<State>) -> crate::Result {
        self.as_ref().call(request).await
    }
}
