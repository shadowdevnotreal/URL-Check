# 🎉 Contributing to WebCheck

First off, **THANK YOU!** 🙌 You're awesome for wanting to contribute to WebCheck!

We love contributors and we want to make your experience as smooth as possible. Whether you're fixing a typo, adding a feature, or optimizing performance, we're excited to have you here!

---

## 🌟 Ways to Contribute

There are many ways to contribute to WebCheck:

### 🐛 Found a Bug?
- Check if it's already reported in [Issues](https://github.com/shadowdevnotreal/URL-Check/issues)
- If not, create a new issue with:
  - A catchy title 🎯
  - Steps to reproduce 🔄
  - Expected vs actual behavior 🤔
  - Your environment (OS, Python version) 💻
  - Screenshots if applicable 📸

### 💡 Have an Idea?
- Open an issue with the `enhancement` label
- Describe your feature idea clearly
- Explain why it would be useful
- Bonus points for mockups or examples! 🎨

### 📝 Improve Documentation?
- Fix typos (we all make them!)
- Clarify confusing sections
- Add examples
- Translate to other languages 🌍

### 🚀 Submit Code?
- Fork the repo
- Create a feature branch
- Make your changes
- Submit a PR (see below)

---

## 🎯 Getting Started

### 1. Fork & Clone
```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/URL-Check
cd URL-Check
```

### 2. Set Up Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest black flake8 mypy
```

### 3. Create a Branch
```bash
# Use descriptive branch names
git checkout -b feature/amazing-new-feature
# or
git checkout -b fix/nasty-bug
```

---

## 💻 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 (we use `black` for formatting)
- **Line Length**: 100 characters max
- **Type Hints**: Add them where possible
- **Docstrings**: Use them for functions and classes

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=webcheck

# Run specific test
pytest tests/test_specific.py
```

### Code Formatting
```bash
# Format with black
black webcheck.py webcheck_web.py

# Check with flake8
flake8 webcheck.py

# Type check with mypy
mypy webcheck.py
```

---

## 🎨 Commit Messages

We love clean commit history! Please use descriptive commit messages:

### Good Commit Messages ✅
```
Add retry logic with exponential backoff
Fix SSL verification bug in async_http_check
Update README with web interface examples
Improve error handling for DNS lookups
```

### Not-So-Good Commit Messages ❌
```
fix stuff
update
wip
asdfasdf
```

### Commit Message Format
```
<type>: <short description>

<optional longer description>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat: Add WebSocket support for live monitoring

Implements WebSocket endpoint for real-time URL status updates.
Includes client-side JavaScript for automatic reconnection.

Closes #42
```

---

## 📋 Pull Request Process

### Before Submitting
- ✅ Code follows style guidelines
- ✅ Tests pass
- ✅ Documentation updated (if needed)
- ✅ CHANGELOG updated (for significant changes)
- ✅ No merge conflicts

### PR Template
When you submit a PR, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How did you test this?

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] My code follows the style guidelines
- [ ] I've added tests
- [ ] I've updated documentation
- [ ] All tests pass
```

### Review Process
1. **Automated Checks**: CI will run tests and linting
2. **Code Review**: Maintainers will review your code
3. **Feedback**: We might request changes
4. **Merge**: Once approved, we'll merge! 🎉

---

## 🏆 Recognition

Contributors get:
- ✨ Your name in the README contributors section
- 🎖️ A shoutout in the release notes
- 🙏 Our eternal gratitude
- ⭐ Good karma points

---

## 🚀 Feature Ideas

Looking for inspiration? Here are some features we'd love to see:

### High Priority
- [ ] Proxy support for requests
- [ ] WebSocket support for live monitoring
- [ ] Database storage for historical data
- [ ] Notification webhooks (Slack, Discord, etc.)
- [ ] API rate limiting per domain
- [ ] Custom headers per URL

### Medium Priority
- [ ] Screenshot capture
- [ ] Response time trending
- [ ] Scheduled monitoring
- [ ] Docker container
- [ ] GraphQL endpoint checking
- [ ] Performance recommendations

### Fun Ideas
- [ ] ASCII art progress indicators
- [ ] Sound effects for success/failure
- [ ] Dark mode for web interface
- [ ] Gamification (badges, achievements)
- [ ] Integration with status page services
- [ ] AI-powered failure diagnosis

---

## 🐛 Bug Bounty

We don't have a formal bug bounty program, but we'll give you:
- 🏅 Credit in the release notes
- ☕ A virtual coffee (or a real one if you're nearby!)
- 🎉 Eternal appreciation

---

## 💬 Communication

### Where to Ask Questions?
- **General Questions**: [GitHub Discussions](https://github.com/shadowdevnotreal/URL-Check/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/shadowdevnotreal/URL-Check/issues)
- **Security Issues**: Email (see SECURITY.md)

### Code of Conduct
Be excellent to each other! 🤘

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):
- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

---

## 📚 Resources

### Learning Resources
- [Python Asyncio Docs](https://docs.python.org/3/library/asyncio.html)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### Useful Tools
- [Black](https://github.com/psf/black) - Code formatter
- [pytest](https://docs.pytest.org/) - Testing framework
- [mypy](http://mypy-lang.org/) - Static type checker

---

## 🎓 First Time Contributing?

Welcome! We love first-time contributors! Here are some good first issues:

**Look for issues labeled:**
- `good first issue` - Perfect for beginners
- `help wanted` - We need help here!
- `documentation` - Great for getting started

### Tips for First-Timers
1. Don't be afraid to ask questions!
2. Start small (fix a typo, add a test)
3. Read the code to understand the structure
4. Test your changes thoroughly
5. Have fun! 🎉

---

## 🎯 Development Workflow

### Typical Development Cycle
```bash
# 1. Update your fork
git checkout main
git pull upstream main

# 2. Create a feature branch
git checkout -b feature/my-awesome-feature

# 3. Make changes
# ... code code code ...

# 4. Test your changes
pytest
black webcheck.py
flake8 webcheck.py

# 5. Commit with descriptive message
git add .
git commit -m "feat: Add my awesome feature"

# 6. Push to your fork
git push origin feature/my-awesome-feature

# 7. Create a Pull Request
# Go to GitHub and create PR from your branch
```

---

## 🌈 Have Fun!

Contributing should be fun! Don't stress about making everything perfect. We're here to help and we appreciate every contribution, no matter how small!

**Remember:**
- Every expert was once a beginner 🌱
- Mistakes are learning opportunities 📚
- Questions are welcome! 💬
- You're awesome! 🌟

---

## 💚 Thank You!

Thank you for taking the time to contribute to WebCheck! You're making the internet a better place, one URL at a time! 🚀

---

**Questions?** Open an issue or start a discussion. We're friendly, we promise! 😊

**Happy Coding!** 💻✨
