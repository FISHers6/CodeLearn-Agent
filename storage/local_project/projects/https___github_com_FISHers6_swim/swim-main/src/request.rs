use std::mem;
use http::{HeaderMap, HeaderValue};
use hyper::Body;
use route_recognizer::Params;
use serde::de::DeserializeOwned;
use crate::body::{is_json_content_type, parse_to_json};

pub struct Request<State> {
    request: hyper::Request<hyper::body::Body>,
    state: State,
    params: Params,
}

impl<State> Request<State> {
    pub fn from_http(
        request: hyper::Request<hyper::body::Body>,
        state: State,
        params: Params,
    ) -> Self {
        Self {
            request,
            state,
            params,
        }
    }

    pub fn method(&self) -> &http::method::Method {
        self.request.method()
    }

    pub fn url(&self) -> String {
        self.request.uri().path().to_owned()
    }

    pub fn params(&self) -> &Params {
        &self.params
    }

    pub fn headers(&self) -> &HeaderMap<HeaderValue> {
        &self.request.headers()
    }

    // todo 实现错误处理 rejection
    pub async fn parse_json<T: DeserializeOwned>(&mut self) -> anyhow::Result<T> {
        // 1.判断content_type是否支持json
        // 2.从header中取二进制bytes
        // 3.反序列化成具体的类型T
        if is_json_content_type(self.headers()) {
            // todo body to_bytes消耗body的所有权, 只能被parse一次
            parse_to_json(mem::replace(self.request.body_mut(), Body::empty())).await
        }else {
            Err(anyhow::anyhow!("rejection: not json content"))
        }
    }
}
