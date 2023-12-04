use crate::handler::Handler;
use http::method::Method;
use route_recognizer::{Match, Router as Recognizer};
use std::collections::HashMap;
use std::sync::Arc;

pub struct Router<State> {
    inner: Arc<RouterInner<State>>,
}

impl<State: Clone + Send + Sync + 'static> Router<State> {
    pub fn new() -> Self {
        Router {
            inner: Arc::new(RouterInner {
                routers: HashMap::new(),
            }),
        }
    }

    fn mut_inner(&mut self) -> &mut RouterInner<State> {
        Arc::get_mut(&mut self.inner).expect("can not found router")
    }

    pub fn route<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        method: Method,
        path: S,
        handler: F,
    ) {
        self.mut_inner()
            .routers
            .entry(method)
            .or_insert(Recognizer::new())
            .add(path.as_ref(), Box::new(handler));
    }

    pub fn get<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::GET, path, handler)
    }

    pub fn post<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::POST, path, handler)
    }

    pub fn put<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::PUT, path, handler)
    }

    pub fn delete<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::DELETE, path, handler)
    }

    pub fn head<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::HEAD, path, handler)
    }

    pub fn options<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::OPTIONS, path, handler)
    }

    pub fn patch<S: AsRef<str>, F: Handler<State>>(
        &mut self,
        path: S,
        handler: F,
    ) {
        self.route(Method::PATCH, path, handler)
    }


    pub fn find<S: AsRef<str>>(
        &self,
        path: S,
        method: &Method,
    ) -> Option<Match<&Box<dyn Handler<State>>>> {
        self.inner
            .routers
            .get(method)
            .and_then(|router| router.recognize(path.as_ref()).ok())
    }
}

pub struct RouterInner<State> {
    routers: HashMap<Method, Recognizer<Box<dyn Handler<State>>>>,
}
