# Contributing to GLChat SDK

Thanks for your interest in contributing! We welcome bug reports, feature requests, and pull requests to improve the SDK.

## Getting Started

1. Fork the repository
2. Clone your fork

```bash
git clone https://github.com/glchat-sdk.git
cd js/glchat-js
```

3. **Install dependencies**

> [!NOTE]
> This repository uses `npm`. Other package managers may work but are not officially supported for development.

```bash
npm install
```

4. **Run the project locally**

```bash
npm build
npm test
```

## Rule of Thumb

- Keep your changes focused and minimal
- Write clear, descriptive commit messages
- Follow existing code style, structure, and linting rules. Please run `npm lint` before submitting a pull request.
- All tests **must** pass.
- Ensure that test coverage remains about 90%.
- Ensure that all codes are runtime-agnostic. Use Web Standard API as much as possible. If it's not possible, use adapter via `navigator.userAgent` to detect the runtime and provide appropriate adapter.

## Testing

Ensure that all tests pass and write new tests for any features or bug fixes:

```bash
npm test
```

## Code Coverage

This project uses **Vitest** with **c8** for coverage reporting.

To check coverage locally:

```bash
npm test:coverage
```

This will generate a summary in the terminal and output a full HTML report in the `coverage/` folder. Open it in your browser to explore uncovered lines:

```bash
open coverage/index.html
```

> ✅ Please make sure new features or fixes include test coverage where applicable.


## Submitting a Pull Request

1. Create a new branch:

```bash
git checkout -b <prefix>/<branch_name>
```

2. Make your changes
3. Push to your fork and open a pull request against `main`
4. Describe your changes clearly in the PR description
