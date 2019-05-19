#! /usr/bin/env bash

wrk -t50 -c100 -d20s http://0.0.0.0:5000/events/kukuu?since=12106650-4e49-47bd-b93a-0b59a7217497
