# Broker Integration Data Directory

This directory contains data files used by the broker integration module.

## Purpose

- Store cached market data for offline testing
- Store serialized broker state for recovery
- Maintain logs specific to broker operations
- Hold test fixtures for broker integration testing

## Usage

The data in this directory is typically managed by the broker integration classes and should not be modified manually unless for testing or debugging purposes.

## Structure

- `cached/` - Cached market data for offline use
- `logs/` - Broker-specific logs
- `state/` - Serialized broker state for recovery
- `test/` - Test fixtures and mock data

The data here is not intended to be committed to version control and may be generated or updated during runtime. 