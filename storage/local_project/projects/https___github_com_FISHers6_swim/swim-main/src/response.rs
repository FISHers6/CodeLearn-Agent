use hyper::{Body, StatusCode};
use std::convert::TryInto;

pub struct Response {
    pub response: hyper::Response<Body>,
}

impl Response {
    pub fn new() -> Self {
        let response = hyper::Response::builder()
            .status(StatusCode::OK)
            .body(Body::empty())
            .unwrap_or(hyper::Response::default());
        Response { response }
    }

    pub fn set_status<S: TryInto<StatusCode>>(&mut self, status: S) {
        *self.response.status_mut() = status
            .try_into()
            .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);
    }

    pub fn internal_server_error(_err: hyper::Error) -> Self {
        let response = hyper::Response::builder()
            .status(StatusCode::INTERNAL_SERVER_ERROR)
            .body(Body::empty())
            .unwrap_or(hyper::Response::default());
        Response { response }
    }
}

impl From<Response> for hyper::Response<Body> {
    fn from(response: Response) -> Self {
        response.response
    }
}
