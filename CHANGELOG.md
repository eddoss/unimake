# Changelog
All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [v0.1.2] - 2024-04-19
### Fixed
- Make core properties boolable

## [v0.1.1] - 2024-04-19
### Fixed
- Make `.unimake/remotes.py` optional

## [v0.1.0] - 2024-04-19
### Features
- Add `umk inspect` to inspect project
- Add `umk config clean` to remove saved config file
- Add `umk config inspect` to print default config details
- Add `umk config presets` to print config presets
- Add `umk config save` to save project config
- Add `umk config write` to write entry inside config file
### Add
- Add `pydantic` based data modeling
- Add runtime container to load `.unimake` to
- Add `.unimake` loading and construction ordering
- Add `docker` adapter based on `python-on-whales`
### Changed
- Merge `umk` and `unimake` to single application `umk`
- Separate `framework` user interfaces to `kit`