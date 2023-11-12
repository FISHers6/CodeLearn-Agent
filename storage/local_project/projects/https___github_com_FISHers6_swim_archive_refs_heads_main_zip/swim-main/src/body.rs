use http::{header, HeaderMap};
use hyper::Body;
use hyper::body::Buf;
use serde::de::DeserializeOwned;

pub(crate) fn is_json_content_type(headers_map: &HeaderMap) -> bool {
    headers_map.get(header::CONTENT_TYPE).map_or(false, |header_value| {
        header_value.to_str().map_or(false, |header_value_str| {
            header_value_str.parse::<mime::Mime>().map_or(false, |mime| {
                mime.type_().eq(&mime::APPLICATION)
                    && (mime.subtype().eq(&mime::JSON) || mime.suffix().map_or(false, |name| name.eq(&mime::JSON)))
            })
        })
    })
}


/// todo body to_bytes消耗body的所有权, 只能被parse一次
pub(crate) async fn parse_to_json<T: DeserializeOwned>(body: Body) -> anyhow::Result<T>  {
    let mut bytes = hyper::body::to_bytes(body).await.map_err(|_err| {
        // todo 错误处理
        anyhow::anyhow!("Body to bytes Error")
    })?;
    serde_json::from_slice(&bytes.copy_to_bytes(bytes.remaining())).map_err(|_err| {
        // todo 错误处理
        anyhow::anyhow!("Body parse to type Error")
    })
}