# dotdeploy

> Minimal dotfiles manager with profile switching and remote backup support.

---

## Installation

```bash
pip install dotdeploy
```

Or install from source:

```bash
git clone https://github.com/yourname/dotdeploy.git && cd dotdeploy && pip install .
```

---

## Usage

Initialize a new dotdeploy repository in your home directory:

```bash
dotdeploy init
```

Add a dotfile and track it under a profile:

```bash
dotdeploy add ~/.bashrc --profile work
```

Switch between profiles:

```bash
dotdeploy switch home
```

Push your dotfiles to a remote backup:

```bash
dotdeploy push origin
```

List all tracked files and active profile:

```bash
dotdeploy status
```

---

## Configuration

dotdeploy reads from `~/.dotdeploy/config.toml`. A minimal example:

```toml
[remote]
url = "git@github.com:yourname/dotfiles.git"

[profile]
default = "home"
```

---

## License

MIT © [yourname](https://github.com/yourname)