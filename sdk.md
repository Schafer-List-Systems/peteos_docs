# SDK: PeteOS Kit

PeteOS Kit is a collection of agentic building blocks for streams, text, and images.

It provides ready-to-use agentic objects you can inherit, compose, and deploy without building from scratch.

## Subpackages

- **`peteos_kit.stream`** — stream buffering, pattern matching, shell execution, and network connections
- **`peteos_kit.text`** — buffer management, text editing, and web navigation
- **`peteos_kit.image`** — image buffers, camera observation, and screen capture

## Quick Start

```python
from peteos import AgenticObject
from peteos_kit import RegexStreamObserver, StreamForwarder

# Create a composed agent
class LogMonitor(RegexStreamObserver, StreamForwarder, AgenticObject):
    """You monitor log streams for patterns and forward interesting entries."""

# Use it
monitor = LogMonitor()
result = await monitor.invoke_agent("Set up a pattern for ERROR messages in my syslog stream.")
print(result)
```

## Key Components

```mermaid
---
title: PeteOS Kit — Agentic Class Inheritance Hierarchy
---
classDiagram
    direction TB

    class BufferManager {
        <<AgenticObject>>
    }

    class StreamBufferManager {
        <<AgenticObject>>
    }

    class StreamObserver {
        <<AgenticObject>>
    }

    class StreamForwarder {
        <<AgenticObject>>
    }

    class RegexStreamObserver {
        <<AgenticObject>>
    }

    class Basher {
        <<AgenticObject>>
    }

    class SandboxedBasher {
        <<AgenticObject>>
    }

    class Connector {
        <<AgenticObject>>
    }

    class TextEditor {
        <<AgenticObject>>
    }

    class WebScraper {
        <<AgenticObject>>
    }

    class WebCapture {
        <<AgenticObject>>
    }

    class NumPyBufferManager {
        <<AgenticObject>>
    }

    class ImageBufferManager {
        <<AgenticObject>>
    }

    class CameraObserver {
        <<AgenticObject>>
    }

    class Screenshooter {
        <<AgenticObject>>
    }

    class DiskImageLoader {
        <<AgenticObject>>
    }

    %% Base hierarchy
    BufferManager <|-- StreamBufferManager
    StreamBufferManager <|-- StreamObserver

    %% Action & shell agents on streams
    StreamBufferManager <|-- StreamForwarder
    StreamBufferManager <|-- Basher
    StreamBufferManager <|-- Connector
    Basher <|-- SandboxedBasher

    %% Pattern matchers
    StreamObserver <|-- RegexStreamObserver

    %% Text agents
    BufferManager <|-- TextEditor
    BufferManager <|-- WebScraper

    %% Image agents
    NumPyBufferManager <|-- ImageBufferManager
    ImageBufferManager <|-- CameraObserver
    ImageBufferManager <|-- Screenshooter
    ImageBufferManager <|-- DiskImageLoader
    ImageBufferManager <|-- WebCapture
```

- **`BufferManager`** — in-memory text buffers with search, diff, and edit
- **`StreamBufferManager`** — rolling, append-only stream buffers with rule-based routing
- **`StreamObserver`** — observes streams and surfaces unexpected entries to the agent
- **`RegexStreamObserver`** — regex-based pattern matchers as conditions for stream rules
- **`TextEditor`** — file editing backed by a multi-file buffer
- **`WebScraper`** — web scraping: fetch and parse web pages into structured buffers
- **`ImageBufferManager`** — numpy-backed image buffers
- **`CameraObserver`** — multi-camera observation with buffer management
- **`Screenshooter`** — screen capture into image buffers
- **`DiskImageLoader`** — load and save image buffers to and from disk
- **`WebCapture`** — capture web pages as images and load web images into image buffers
- **`Basher`** / **`SandboxedBasher`** — shell execution with buffer integration

## Installation and Configuration

For setup instructions please consult [https://github.com/Schafer-List-Systems/petekit](https://github.com/Schafer-List-Systems/petekit).

