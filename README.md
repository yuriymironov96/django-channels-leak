# django-channels-leak

This project is a full copy of django_channels tutorial from the official doc: https://channels.readthedocs.io/en/stable/tutorial/index.html
The only changes are some commented out debug statements for memory tracing.

## Deploy locally

### Prerequisites

You will need a backend for channels_layer - `Redis` or `Rabbitmq`. Repo includes settings and configuration for both.
All the dependencies can be installed using `Poetry`, they also include debug libraries like `Pympler`.

### Setup

- Activate your local environemnt;
- Go to `<project_root>/channels_leak`;
- Run `daphne channels_leak.asgi:application`;

## Steps to reproduce

- Run server locally;
- Identify PID and remember the RAM consumption before any tab is open;
- Open multiple tabs of a single chat room, like `http://127.0.0.1:8000/chat/hello/` (approximately ten);
- Close all the tabs;
- Check RAM consumption. It has not been reduced, or has been reduced only by ~half since the peak amount.

## Sample metrics from local debug

- Server is launched, no browser tabs open: 49.3 MB;
- First broser tab opened: 51.2 MB;
- 20 browser tabs opened: 52.2 MB;
- All browser tabs closed: 52.2 MB;
- 20 browser tabs opened: 52.6 MB;
- All browser tabs closed: 52.6 MB;

## Possible locations of memory leak

Consumer instance has channels_layer property, and it looks like it leaks whatever the backend is. Both for `Redis` and `Rabbitmq` the commection map is growing larger after each tab opened.

This object's memory usage is reduced after closing tabs, but it still consumes more memory (+50-100 KB) after opening and closing multiple tabs.
