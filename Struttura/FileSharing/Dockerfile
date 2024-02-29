FROM golang:1.21

# Set destination for COPY
WORKDIR /app

# Copy all files
COPY ./ ./

# Download Go modules
RUN go mod download

# Build
RUN go build -o /file-server

EXPOSE 8080

# Run
CMD ["/file-server"]