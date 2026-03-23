# DevOps and MLOps — Midterm Practical Exam

**Sessions 1–6 | Duration: 1.5 hours**

---

## Exam Setup (no points — do this first, ~10 minutes)

1. **Download** the `devops-midterm-exam.tar.gz` file from eCampus
2. **Extract** it:
   ```bash
   tar xzf devops-midterm-exam.tar.gz
   cd devops-midterm-exam
   ```
3. **Create a private GitHub repository** named `devops-midterm-exam` under your personal account (use your ESADE email if possible)
4. **Initialize and push:**
   ```bash
   git init
   git add .
   git commit -m "feat: initial exam project"
   git remote add origin https://github.com/YOUR-USERNAME/devops-midterm-exam.git
   git branch -M main
   git push -u origin main
   ```
5. **Invite the professor** as a collaborator: go to your repo Settings → Collaborators → Add `joseporiolrius`

> **Important:** Your repository **must be private**. Public repositories will not be graded.

---

## Exam Overview

You have inherited a project: **devops-midterm-exam** — a Mock OpenAI-compatible API built with FastAPI. The application implements the OpenAI chat completions interface and is designed to run alongside **OpenWebUI** as its frontend.

The previous developer left in a hurry — some files are broken, others are missing entirely. Your job is to **fix what's broken** and **build what's missing** so the full deployment chain works.

**Architecture:**

```
OpenWebUI (:80) --> Mock API (:8080/v1) --> "Point to a real API!"
```

---

## Rubric

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Working implementation** | 50% | Fixed files would actually work if deployed. Written files are syntactically correct and functional. |
| **Troubleshooting & diagnosis** | 30% | Errors are correctly identified. Fixes address root causes, not symptoms. Comments explain what was wrong. |
| **Best practices & security** | 20% | Solutions follow DevOps best practices covered in class (idempotency, least privilege, no hardcoded secrets, proper tagging, etc.). |

### Grading Scale

| Points | Grade |
|--------|-------|
| 90–100 | Excellent — all files correct, best practices applied, clear diagnosis |
| 70–89 | Good — most fixes correct, minor issues in implementation |
| 50–69 | Adequate — core errors found, implementations partially correct |
| 30–49 | Insufficient — several errors missed, significant implementation gaps |
| 0–29 | Very insufficient — fundamental misunderstanding of concepts |

---

## Part 1 — Troubleshooting: Fix the Broken Files (40 points)

Each file contains **intentional errors**. Find them, fix them, and add a short comment above each fix explaining what was wrong and why.

---

### Exercise 1A — Fix the Dockerfile (12 points)

The following Dockerfile builds the Mock OpenAI API. It has **4 errors** (3 points each).

```dockerfile
FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV API_KEY=sk-secret-key-do-not-share
EXPOSE 8000
CMD python src/main.py
```

**Context:** The real project uses `uv` for package management and `pyproject.toml` (not `requirements.txt`). The app is installed as a package with a console script entry point `mock-openai-api`.

**Instructions:**
1. Write your fixed Dockerfile to `solutions/part1/1a-dockerfile/Dockerfile`
2. Add a `# FIX:` comment above each line you changed explaining the problem
3. Build the image to verify it works: `docker build -t mock-openai-api:exam -f solutions/part1/1a-dockerfile/Dockerfile .`
4. Take a screenshot of the successful build output and save it as `solutions/part1/1a-dockerfile/docker-build.png`
5. Commit, tag and push: `git add . && git commit -m "part1a" && git tag part1a && git push origin main --tags`

---

### Exercise 1B — Fix the CloudFormation Template (16 points)

The following CloudFormation template should deploy an EC2 instance where we can run the Mock API (:8080) and OpenWebUI (:80), accessible via SSH. It has **4 errors** (4 points each).

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Mock OpenAI API infrastructure

Parameters:
  KeyName:
    Type: String
    Description: SSH key pair name

Resources:
  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Allow web traffic
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3a.small
      ImageId: ami-0e9085e60087ce171
      SecurityGroupIds:
        - !Ref WebSecurityGroup

Outputs:
  InstanceId:
    Description: EC2 Instance ID
    Value: !Ref WebServer
```

**Hint:** Think about what ports the services actually use (Mock API on 8080, OpenWebUI on 80). Think about how you'll **connect** to this server with Ansible. Think about what information you need **after** the stack is created to configure your Ansible inventory.

**Instructions:**
1. Write your fixed template to `solutions/part1/1b-cloudformation/template.yml`
2. Add a `# FIX:` comment above each line or block you changed
3. Take a screenshot of your git diff or the fixed file in your editor showing the changes, save it as `solutions/part1/1b-cloudformation/git-diff.png`
4. Commit, tag and push: `git add . && git commit -m "part1b" && git tag part1b && git push origin main --tags`

---

### Exercise 1C — Fix the Ansible Playbook (12 points)

The following playbook should install Docker and deploy the Mock API + OpenWebUI on a remote server. It has **4 errors** (3 points each).

```yaml
- name: Deploy Mock OpenAI API
  hosts: mock-openai-api
  become: false

  tasks:
    - name: Install Docker
      ansible.builtin.shell:
        cmd: apt-get install -y docker-ce

    - name: Create application directory
      ansible.builtin.file:
        path: /opt/mock-openai-api
        state: directory

    - name: Deploy docker-compose file
      ansible.builtin.template:
        src: docker-compose.yml.j2
        dest: /opt/mock-openai-api/docker-compose.yml
      notify: Restart app

    - name: Start services
      community.docker.docker_compose_v2:
        project_src: /opt/mock-openai-api
        state: present

  handlers:
    - name: Restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

**Instructions:**
1. Write your fixed playbook to `solutions/part1/1c-ansible/playbook.yml`
2. Add a `# FIX:` comment above each line you changed
3. Take a screenshot of your git diff or the fixed file showing the changes, save it as `solutions/part1/1c-ansible/git-diff.png`
4. Commit, tag and push: `git add . && git commit -m "part1c" && git tag part1c && git push origin main --tags`

---

## Part 2 — Implementation: Build the Missing Pieces (60 points)

Write the following files from scratch. They must be syntactically correct and follow the best practices taught in class.

---

### Exercise 2A — Write a docker-compose.yml (22 points)

The deployment requires two services running together:

- The **Mock OpenAI API** from GHCR (`ghcr.io/oriolrius/devops-midterm-exam:v1`), exposed on port **8080**, with a health check on `/health`
- **OpenWebUI** (`ghcr.io/open-webui/open-webui:main`), exposed on port **80** (container listens on 8080), pre-configured to point to the Mock API via the environment variable `OPENAI_API_BASE_URL`
- OpenWebUI data must **persist** across container restarts using a named volume
- OpenWebUI should **wait** for the Mock API to be healthy before starting

Write a complete `docker-compose.yml`.

| Criteria | Points |
|----------|--------|
| Both services defined with correct images | 4 |
| Port mappings correct (8080 for API, 80:8080 for OpenWebUI) | 4 |
| `OPENAI_API_BASE_URL` pointing to `http://mock-api:8000/v1` (internal container port) | 4 |
| Named volume for OpenWebUI data persistence | 4 |
| `depends_on` with health check condition for startup order | 4 |
| Restart policy and health check on the Mock API service | 2 |

**Instructions:**
1. Write your file to `solutions/part2/2a-compose/docker-compose.yml`
2. Run it: `docker compose -f solutions/part2/2a-compose/docker-compose.yml up -d`
3. Take a screenshot of `docker compose ps` showing both containers running and save it as `solutions/part2/2a-compose/compose-ps.png`
4. Open OpenWebUI in your browser (http://localhost) and take a screenshot showing the UI loaded, save it as `solutions/part2/2a-compose/openwebui-browser.png`
5. Commit, tag and push: `git add . && git commit -m "part2a" && git tag part2a && git push origin main --tags`

---

### Exercise 2B — Write a GitHub Actions CI Workflow (22 points)

Create a GitHub Actions workflow file (`.github/workflows/ci.yml`) that implements the following pipeline:

- **Triggers** on pull requests to the `main` branch
- **Job 1: `lint`** — Checks out the code, sets up uv, installs dev dependencies, runs `ruff check` and `ruff format --check` on `src/` and `tests/`
- **Job 2: `test`** — Checks out the code, sets up uv, installs dev dependencies, runs `pytest -v`
- **Job 3: `docker`** — Only runs if both `lint` and `test` pass. Builds the Docker image and pushes it to GitHub Container Registry (ghcr.io). Uses `docker/login-action` and `docker/build-push-action`.

| Criteria | Points |
|----------|--------|
| Correct trigger on pull requests to main | 2 |
| `lint` job: checkout + setup-uv + ruff check + ruff format --check | 4 |
| `test` job: checkout + setup-uv + pytest | 4 |
| `docker` job: depends on both `lint` and `test` via `needs` | 3 |
| Docker registry login using `secrets.GITHUB_TOKEN` with ghcr.io | 4 |
| Docker build and push with correct Dockerfile path and image name | 3 |
| Correct YAML syntax and structure throughout | 2 |

**Instructions:**
1. Write your workflow to `solutions/part2/2b-cicd/.github/workflows/ci.yml`
2. Also copy it to `.github/workflows/ci.yml` in the project root so GitHub can detect it
3. Push to your repo and take a screenshot of the GitHub Actions tab showing the workflow file (or a triggered run), save it as `solutions/part2/2b-cicd/github-actions.png`
4. Commit, tag and push: `git add . && git commit -m "part2b" && git tag part2b && git push origin main --tags`

---

### Exercise 2C — Write the Ansible Deployment Files (16 points)

**Scenario:** A CloudFormation stack just finished creating an EC2 instance for the Mock OpenAI API. The stack outputs show:

```
PublicIp: 54.78.100.25
```

The SSH user is `ubuntu`, the private key is at `~/.ssh/deploy-key.pem`, and you need to automate the connection for a CI/CD pipeline (no interactive prompts).

**Task 1:** Write `inventory.ini` (10 points)

| Criteria | Points |
|----------|--------|
| Host entry with correct IP address | 3 |
| Correct `ansible_user` | 3 |
| Correct `ansible_ssh_private_key_file` | 2 |
| Proper group name and valid INI format | 2 |

**Task 2:** Write `ansible.cfg` (6 points)

| Criteria | Points |
|----------|--------|
| Points to the correct inventory file | 2 |
| Disables host key checking (required for automation) | 2 |
| Sets the correct default remote user | 2 |

**Instructions:**
1. Write your files to `solutions/part2/2c-ansible/inventory.ini` and `solutions/part2/2c-ansible/ansible.cfg`
2. Take a screenshot of your GitHub repo showing the files committed, save it as `solutions/part2/2c-ansible/github-repo.png`
3. Commit, tag and push: `git add . && git commit -m "part2c" && git tag part2c && git push origin main --tags`

---

## Summary

| Exercise | Topic | Points |
|----------|-------|--------|
| **Part 1 — Troubleshooting** | | **40** |
| 1A. Fix the Dockerfile | Docker | 12 |
| 1B. Fix the CloudFormation template | IaC | 16 |
| 1C. Fix the Ansible playbook | Ansible | 12 |
| **Part 2 — Implementation** | | **60** |
| 2A. Write docker-compose.yml | Docker + OpenWebUI | 22 |
| 2B. Write GitHub Actions workflow | CI/CD | 22 |
| 2C. Write Ansible deployment files | Ansible + IaC | 16 |
| **Total** | | **100** |

---

## Submission — Two Deliveries Required

### 1. GitHub Repository

- Your repo must be **private** with `joseporiolrius` invited as collaborator
- Must contain **6 git tags**: `part1a`, `part1b`, `part1c`, `part2a`, `part2b`, `part2c`
- Push all your work: `git push origin main --tags`

### 2. eCampus Upload

- Create a tar.gz of your **entire project folder** (including the `solutions/` directory with screenshots):
  ```bash
  cd ..
  tar czf devops-midterm-YOURNAME.tar.gz devops-midterm-exam/
  ```
- Upload `devops-midterm-YOURNAME.tar.gz` to the eCampus exam assignment

### Required Screenshots

| Exercise | Screenshot file | What it shows |
|----------|----------------|---------------|
| 1A | `solutions/part1/1a-dockerfile/docker-build.png` | Successful `docker build` output |
| 1B | `solutions/part1/1b-cloudformation/git-diff.png` | Git diff or editor showing your fixes |
| 1C | `solutions/part1/1c-ansible/git-diff.png` | Git diff or editor showing your fixes |
| 2A | `solutions/part2/2a-compose/compose-ps.png` | `docker compose ps` with both containers running |
| 2A | `solutions/part2/2a-compose/openwebui-browser.png` | OpenWebUI loaded in browser at localhost |
| 2B | `solutions/part2/2b-cicd/github-actions.png` | GitHub Actions tab showing the workflow |
| 2C | `solutions/part2/2c-ansible/github-repo.png` | GitHub repo showing committed files |

### Required Git Tags

| Tag | After completing |
|-----|-----------------|
| `part1a` | Exercise 1A (Dockerfile fix) |
| `part1b` | Exercise 1B (CloudFormation fix) |
| `part1c` | Exercise 1C (Ansible fix) |
| `part2a` | Exercise 2A (docker-compose) |
| `part2b` | Exercise 2B (GitHub Actions) |
| `part2c` | Exercise 2C (Ansible files) |

> **Anti-cheating notice:** The eCampus submission and GitHub repository must match. Git tags, commit timestamps, and screenshots will be verified.

### Solution files must follow this structure

```
solutions/
  part1/
    1a-dockerfile/
      Dockerfile
      docker-build.png
    1b-cloudformation/
      template.yml
      git-diff.png
    1c-ansible/
      playbook.yml
      git-diff.png
  part2/
    2a-compose/
      docker-compose.yml
      compose-ps.png
      openwebui-browser.png
    2b-cicd/
      .github/workflows/ci.yml
      github-actions.png
    2c-ansible/
      inventory.ini
      ansible.cfg
      github-repo.png
```

- All fixes must include `# FIX:` comments explaining the error
- All implementations must be syntactically valid YAML / Dockerfile / INI
