use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;

use async_trait::async_trait;

use crate::chain::Chain;
use crate::request::Request;

#[async_trait]
pub trait Middleware<State>: Send + Sync + 'static {
    async fn handle(&self, request: Request<State>, chain: Chain<'_, State>) -> crate::Result;
}

#[async_trait]
impl<State, F> Middleware<State> for F
where
    State: Clone + Send + Sync + 'static,
    F: Send
        + Sync
        + 'static
        + for<'a> Fn(
            Request<State>,
            Chain<'a, State>,
        ) -> Pin<Box<dyn Future<Output = crate::Result> + 'a + Send>>,
{
    async fn handle(&self, req: Request<State>, chain: Chain<'_, State>) -> crate::Result {
        (self)(req, chain).await
    }
}

#[async_trait]
impl<State: Clone + Send + Sync + 'static> Middleware<State> for Arc<dyn Middleware<State>> {
    async fn handle(&self, request: Request<State>, chain: Chain<'_, State>) -> crate::Result {
        self.as_ref().handle(request, chain).await
    }
}
