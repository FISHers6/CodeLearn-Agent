use crate::handler::Handler;
use crate::middleware::Middleware;
use crate::request::Request;
use crate::response::Response;
use std::sync::Arc;

pub struct Chain<'a, State> {
    pub handler: &'a dyn Handler<State>,
    pub next: &'a [Arc<dyn Middleware<State>>],
}

impl<State: Clone + Send + Sync + 'static> Chain<'_, State> {
    pub async fn call(mut self, request: Request<State>) -> Response {
        if let Some((current_middleware, next_middlewares)) = self.next.split_first() {
            self.next = next_middlewares;
            match current_middleware.handle(request, self).await {
                Ok(response) => response,
                Err(err) => Response::internal_server_error(err),
            }
        } else {
            match self.handler.call(request).await {
                Ok(response) => response,
                Err(err) => Response::internal_server_error(err),
            }
        }
    }
}
