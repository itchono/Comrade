FROM golang:1.15-alpine AS builder

RUN apk --no-cache add ca-certificates git
WORKDIR /go/src/github.com/itchono/Comrade

COPY go.mod .
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 go build -o /go/bin/Comrade

FROM alpine:latest
WORKDIR /app
COPY --from=builder /go/bin/Comrade .
CMD ["./Comrade"]

