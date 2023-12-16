
# 🏊‍♂️ Swim

Swim is a web framework that allows your app to swim on the Internet. It is written in Rust and provides a set of features that are essential for building web applications.

## 🚀 Features

- 🔀 Router: The router module provides methods for routing HTTP requests to their respective handlers. It supports various HTTP methods including GET, POST, PUT, DELETE, HEAD, OPTIONS, and PATCH.

- 🖐 Handler: The handler module defines the Handler trait which is implemented by functions that handle HTTP requests.

- 🔧 Middleware: The middleware module provides the Middleware trait which is implemented by functions that process HTTP requests or responses.

- 📨 Request: The request module provides the Request struct which represents an HTTP request. It provides methods for accessing the request method, URL, parameters, and headers. It also provides a method for parsing the request body as JSON.

- 📩 Response: The response module provides the Response struct which represents an HTTP response. It provides methods for setting the response status and for creating a response with an internal server error status.

- ⛓ Chain: The chain module provides the Chain struct which represents a chain of middleware functions. It provides a method for calling the middleware functions in the chain.

## 📖 Usage

To use Swim, you need to create an instance of the App struct, add routes and middleware to it, and then call the swim method to start the server.

Here is an example:

```rust
let app = App::new()
    .get("/hello", |request: Request<>| async move {
        println!("request: {}", request.url());
        println!("params: {:?}", request.params());
        println!("headers: {:?}", request.headers());
        Ok(Response::new())
    })
    .get("/world", |request: Request<>| async move {
        println!("request: {}", request.url());
        Ok(Response::new())
    })
    .with(Before(|request: Request<>| async move {
        println!("before middleware, request.url: {}", request.url());
        request
    }))
    .with(after)
    .swim("127.0.0.1:8008")
    .await;
```

In this example, the app has two routes ("/hello" and "/world") and two middleware functions (Before and after). The server listens on "127.0.0.1:8008".

## 📜 License

Swim is licensed under the MIT license. See the LICENSE file for more details.e
