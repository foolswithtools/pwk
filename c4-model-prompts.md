# C4 Model Prompts for Claude Code

> A collection of prompts for using Claude Code to understand, analyze, and create C4 architecture diagrams. Copy and customize these prompts for your specific needs.

---

## Table of Contents

1. [Understanding C4 Concepts](#understanding-c4-concepts)
2. [Analyzing Existing Codebases](#analyzing-existing-codebases)
3. [Creating System Context Diagrams](#creating-system-context-diagrams)
4. [Creating Container Diagrams](#creating-container-diagrams)
5. [Creating Component Diagrams](#creating-component-diagrams)
6. [Creating Supplementary Diagrams](#creating-supplementary-diagrams)
7. [Domain-Specific Templates](#domain-specific-templates)
8. [Review and Validation](#review-and-validation)

---

## Understanding C4 Concepts

### Basic C4 Questions

```
Explain the difference between a Container and a Component in C4 terminology.
Provide examples relevant to a [web application / microservices system / mobile app].
```

```
When should I use a System Context diagram vs a Container diagram?
What questions does each answer for stakeholders?
```

```
What is the difference between a Person and a Software System in C4?
Can an API consumer be represented as both?
```

### Choosing the Right Diagram Level

```
I need to document the architecture of [SYSTEM_NAME].
Help me decide which C4 diagram levels I should create based on:
- Audience: [technical team / executives / new developers / external partners]
- Purpose: [onboarding / design review / compliance / troubleshooting]
- System complexity: [monolith / microservices / serverless / hybrid]
```

```
My team is asking for architecture documentation. We have limited time.
Which C4 diagrams provide the most value for the least effort?
Explain your reasoning.
```

---

## Analyzing Existing Codebases

### Codebase Analysis Prompts

```
Analyze this codebase and identify the C4 abstractions:
1. What is the Software System? Describe its purpose.
2. What Containers exist? (deployable units, databases, message queues)
3. For the main application container, what Components can you identify?
4. Who are the People (users/actors) that interact with this system?
5. What external Software Systems does this depend on?
```

```
Explore this repository and create a C4 Container inventory:
- List all containers (applications, services, databases)
- Identify the technology stack for each
- Map the communication patterns between containers
- Note any external integrations

Output as a structured list I can use for a Container diagram.
```

```
Analyze the [directory/package/module] structure of this codebase.
Identify logical components within the [CONTAINER_NAME] container.
For each component, provide:
- Name
- Responsibility (one sentence)
- Technology/Framework used
- Dependencies on other components
```

### Architecture Discovery

```
I'm new to this codebase. Help me understand its architecture:
1. What type of system is this? (web app, API, CLI, etc.)
2. What are the entry points?
3. How is the code organized?
4. What are the main external dependencies?
5. Create a high-level C4 Container description.
```

```
Trace the data flow for [FEATURE/USE_CASE] through this codebase.
Identify which C4 elements (containers, components) are involved.
This will help me create a Dynamic diagram.
```

---

## Creating System Context Diagrams

### Generic System Context Template

```
Create a C4 System Context diagram for [SYSTEM_NAME].

Context:
- System purpose: [DESCRIPTION]
- Primary users: [USER_TYPES]
- External systems: [EXTERNAL_DEPENDENCIES]

Requirements:
1. Place the main system in the center
2. Show all user types as Person elements
3. Show external systems with brief descriptions
4. Label all relationships with verbs describing the interaction
5. Output in [Structurizr DSL / PlantUML / Mermaid] format
6. Include a proper title and legend
```

### System Context with Business Context

```
Create a C4 System Context diagram for [SYSTEM_NAME] that tells the business story.

Business context:
- What problem does this system solve?
- Who benefits from it?
- What would break if this system went down?

Include:
- All user personas with their goals
- All external systems with why they're needed
- Relationship labels that a business stakeholder would understand
```

---

## Creating Container Diagrams

### Generic Container Template

```
Create a C4 Container diagram for [SYSTEM_NAME].

System components:
- Frontend: [TECHNOLOGY]
- Backend: [TECHNOLOGY]
- Database: [TECHNOLOGY]
- Other services: [LIST]

Requirements:
1. Show each container with name, technology, and description
2. Include any message queues, caches, or storage
3. Show relationships with protocols (HTTP, gRPC, SQL, etc.)
4. Include the people and external systems from the Context diagram
5. Output in [Structurizr DSL / PlantUML / Mermaid] format
```

### Container Diagram from Code Analysis

```
Based on your analysis of this codebase, create a C4 Container diagram.

For each container, specify:
- Name (clear, descriptive)
- Technology stack
- Primary responsibility
- How it communicates with other containers

Show all:
- Internal containers (things we build/own)
- External systems (things we integrate with)
- Data stores (databases, caches, file storage)
- Message infrastructure (queues, event buses)
```

### Microservices Container Diagram

```
Create a C4 Container diagram for our microservices architecture.

Services:
[LIST YOUR SERVICES]

For each service, identify:
- Name and bounded context
- Technology stack
- Owned data store (if any)
- APIs exposed
- Events published/consumed

Show communication patterns:
- Synchronous (REST, gRPC)
- Asynchronous (message queues, events)
```

---

## Creating Component Diagrams

### Generic Component Template

```
Create a C4 Component diagram for the [CONTAINER_NAME] container.

The container is a [TECHNOLOGY] application that [PURPOSE].

Based on the codebase structure, identify and show:
1. Major components (controllers, services, repositories, etc.)
2. Component responsibilities
3. Dependencies between components
4. External interfaces (APIs consumed/exposed)

Output in [Structurizr DSL / PlantUML / Mermaid] format.
```

### Component Diagram from Package Structure

```
Analyze the package/directory structure of [CONTAINER_NAME].
Create a C4 Component diagram showing:

1. Logical layers (presentation, business, data)
2. Feature modules or bounded contexts
3. Shared/common components
4. External integrations as separate components

Group related components and show their dependencies.
```

---

## Creating Supplementary Diagrams

### Dynamic Diagram

```
Create a C4 Dynamic diagram showing the [USE_CASE/FEATURE] flow.

Scenario: [DESCRIBE THE USER STORY OR FEATURE]

Requirements:
1. Show the sequence of interactions
2. Number each step
3. Include the relevant containers/components
4. Show the data/messages being passed
5. Use [collaboration / sequence] style
```

### Deployment Diagram

```
Create a C4 Deployment diagram for the [ENVIRONMENT] environment.

Infrastructure:
- Cloud provider: [AWS / Azure / GCP / On-prem]
- Container orchestration: [Kubernetes / ECS / Docker Compose / None]
- Key infrastructure: [Load balancers, CDN, DNS, etc.]

For each container from the Container diagram, show:
- Where it runs (which deployment node)
- Number of instances (if relevant)
- Key configuration

Include infrastructure nodes like load balancers and firewalls.
```

### System Landscape Diagram

```
Create a C4 System Landscape diagram for [ORGANIZATION/DEPARTMENT].

Systems to include:
[LIST ALL SYSTEMS IN SCOPE]

Show:
- All software systems in the landscape
- Key user types across systems
- System-to-system integrations
- Data flows between systems
- Which systems we own vs. external
```

---

## Domain-Specific Templates

### E-Commerce Platform

```
Create C4 diagrams for an e-commerce platform with:

Users: Customers, Administrators, Warehouse Staff
Containers:
- Web storefront (React)
- Mobile app (React Native)
- Order service (Node.js)
- Inventory service (Java)
- Payment service (integration with Stripe)
- Notification service (email/SMS)
- PostgreSQL database
- Redis cache
- RabbitMQ message queue

Create both System Context and Container diagrams.
```

### SaaS Application

```
Create C4 diagrams for a multi-tenant SaaS application.

Users: End Users, Tenant Admins, Platform Admins
Key aspects:
- Multi-tenant data isolation
- Authentication/Authorization (Auth0 integration)
- API for third-party integrations
- Background job processing
- Analytics/Reporting

Create System Context and Container diagrams.
```

### API Platform

```
Create C4 diagrams for an API platform.

Components:
- API Gateway
- Multiple microservices
- Authentication service
- Rate limiting
- API documentation portal
- Developer portal

Show both internal architecture and external API consumers.
```

### Event-Driven System

```
Create C4 diagrams for an event-driven architecture.

Include:
- Event producers
- Event bus/broker (Kafka/RabbitMQ/EventBridge)
- Event consumers
- Event store
- Saga/Choreography patterns

Show both Container diagram and a Dynamic diagram for a key event flow.
```

### Mobile Application Backend

```
Create C4 diagrams for a mobile app backend.

Clients: iOS App, Android App
Backend services: [LIST]
Key features:
- Push notifications
- Offline sync
- Real-time updates (WebSocket)
- Media storage

Show the Container diagram with mobile-specific considerations.
```

---

## Review and Validation

### Diagram Review Prompts

```
Review this C4 [DIAGRAM_TYPE] diagram and check:

1. Title - Is it clear and descriptive?
2. Legend - Are all symbols explained?
3. Elements - Does each have name, type, and description?
4. Relationships - Are all labeled with direction-appropriate text?
5. Scope - Is the boundary clear?
6. Completeness - Are any obvious elements missing?

Provide specific feedback and suggestions for improvement.
```

```
Compare this C4 diagram against the actual codebase.
Identify:
1. Elements in the diagram that don't exist in code
2. Elements in code that are missing from the diagram
3. Relationships that are incorrect or outdated
4. Technology labels that need updating
```

### Architecture Validation

```
Based on this C4 Container diagram, identify potential architectural concerns:

1. Single points of failure
2. Tight coupling between containers
3. Missing security boundaries
4. Scalability bottlenecks
5. Unclear data ownership

Suggest improvements aligned with [specific architecture patterns or requirements].
```

---

## Multi-Diagram Generation

### Complete C4 Documentation Set

```
Create a complete C4 documentation set for [SYSTEM_NAME].

Generate the following in [Structurizr DSL / PlantUML / Mermaid]:

1. System Context diagram - showing all users and external systems
2. Container diagram - showing all containers and their technologies
3. Component diagram for [MAIN_CONTAINER] - showing internal structure
4. Deployment diagram for production - showing infrastructure mapping
5. One Dynamic diagram for [KEY_USE_CASE]

Ensure consistency across all diagrams:
- Same naming conventions
- Same element descriptions
- Proper cross-references between levels
```

### Iterative Refinement

```
I have a draft C4 [DIAGRAM_TYPE] diagram. Help me refine it:

Current diagram:
[PASTE YOUR DIAGRAM CODE]

Questions:
1. Is the abstraction level consistent?
2. Are the descriptions clear and useful?
3. Should any elements be combined or split?
4. Are there missing relationships?
5. Does this follow C4 best practices?

Provide an improved version with explanations for changes.
```

---

## Output Format Preferences

### Structurizr DSL

```
Output all diagrams in Structurizr DSL format.
Use this structure:
- Workspace with meaningful name
- Model section with all elements
- Views section with diagram configurations
- Include autolayout directive
- Add styling/theming if appropriate
```

### PlantUML with C4

```
Output all diagrams in PlantUML format using the C4-PlantUML library.
Include the appropriate !include statements.
Use the standard C4 macros (Person, System, Container, etc.).
Add LAYOUT_WITH_LEGEND() for automatic legend.
```

### Mermaid

```
Output all diagrams in Mermaid format.
Use the C4 diagram syntax (C4Context, C4Container, C4Component).
Ensure compatibility with GitHub markdown rendering.
```

---

## Tips for Effective Prompts

1. **Provide context**: Always describe the domain, technology stack, and purpose
2. **Specify audience**: Who will view these diagrams affects detail level
3. **Name your elements**: Provide specific names rather than generic placeholders
4. **Request specific formats**: Specify Structurizr DSL, PlantUML, or Mermaid
5. **Iterate**: Start with System Context, refine, then add Container details
6. **Validate against code**: Ask Claude to verify diagrams match the actual codebase
7. **Include constraints**: Mention security, scalability, or compliance requirements

---

## Example Workflow

```
# Step 1: Analyze the codebase
"Analyze this codebase and identify all C4 abstractions (systems, containers,
components, people). Create an inventory I can use for diagramming."

# Step 2: Create System Context
"Based on your analysis, create a C4 System Context diagram in Structurizr DSL.
Include all external systems and user types you identified."

# Step 3: Create Container Diagram
"Now create a Container diagram that zooms into the main system.
Show all deployable units, databases, and message infrastructure."

# Step 4: Validate
"Compare these diagrams against the actual code.
Are there any discrepancies or missing elements?"

# Step 5: Refine
"Update the diagrams based on [FEEDBACK].
Ensure the notation follows C4 best practices."
```
