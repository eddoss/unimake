package main

import (
	"fmt"
	"net/http"
    "github.com/labstack/echo/v4"
)

func main() {
	p := 2233
	e := echo.New()
	e.GET("/", func(c echo.Context) error {
		return c.String(http.StatusOK, "Hello, Unimake :)")
	})
	fmt.Printf("Open browser at http://localhost:%v", p)
	e.Logger.Fatal(e.Start(fmt.Sprintf(":%v", p)))
}
