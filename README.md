# PQFE (Post-Quantum File Encryption)

A Python wrapper over liboqs that provides easy-to-use post-quantum file encryption capabilities.

## Overview

PQFE is a tool that allows you to encrypt files using post-quantum cryptographic algorithms implemented in liboqs (Open Quantum Safe). This wrapper makes it simple to protect your files against potential threats from quantum computers.

## Features

- Easy-to-use command line interface
- Support for multiple post-quantum encryption algorithms
- File encryption and decryption
- Built on top of the well-tested liboqs library
- Python-based for cross-platform compatibility
- Multiple symmetric cipher options (AES-256-GCM and ChaCha20-Poly1305)
- In-memory operation support
- Customizable output locations

## Build status
[![Build and Push Docker Image](https://github.com/esola-thomas/pqfe/actions/workflows/push_docker_image.yml/badge.svg)](https://github.com/esola-thomas/pqfe/actions/workflows/push_docker_image.yml)

^ This is a Docker image to be used to create containers for developmenent and testing
