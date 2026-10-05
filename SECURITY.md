# Security notes

- The tool requires no account and no credentials. It reads Brella's public
  event API, which the platform itself exposes for embedding event data.
- No secrets, cookies, or tokens are hardcoded or stored anywhere.
- Never commit pulled CSVs back to the repo; output is gitignored.
- Report vulnerabilities by opening a private security advisory on GitHub.
