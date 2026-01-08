Feature: Chatbot API Service
  As a developer
  I want to interact with various LLM providers through a unified API
  So that I can easily switch between different AI models

  Background:
    Given the chatbot service is running
    And the API is accessible at "http://localhost:8000"

  Scenario: Health check returns service status
    When I send a GET request to "/health"
    Then the response status code should be 200
    And the response should contain "status" field
    And the response should contain "providers" field
    And the "providers" field should be an object

  Scenario: Send a message using Ollama provider
    Given Ollama is running and available
    And the "llama3" model is downloaded in Ollama
    When I send a POST request to "/chat" with:
      | field    | value                          |
      | message  | Hello, how are you?            |
      | provider | ollama                         |
      | model    | llama3                         |
    Then the response status code should be 200
    And the response should contain "response" field
    And the response should contain "provider" field with value "ollama"
    And the response should contain "model" field with value "llama3"
    And the "response" field should not be empty

  Scenario: Send a message using default provider
    Given Ollama is running and available
    When I send a POST request to "/chat" with:
      | field   | value                |
      | message | What is 2 + 2?       |
    Then the response status code should be 200
    And the response "provider" field should be "ollama"
    And the "response" field should contain a number or calculation result

  Scenario: Send a message with OpenAI provider
    Given OpenAI API key is configured
    When I send a POST request to "/chat" with:
      | field    | value                     |
      | message  | Tell me a short joke      |
      | provider | openai                    |
      | model    | gpt-3.5-turbo            |
    Then the response status code should be 200
    And the response "provider" field should be "openai"
    And the response "model" field should be "gpt-3.5-turbo"
    And the "response" field should not be empty

  Scenario: Send a message with Anthropic provider
    Given Anthropic API key is configured
    When I send a POST request to "/chat" with:
      | field    | value                          |
      | message  | Explain quantum computing      |
      | provider | anthropic                      |
      | model    | claude-3-5-sonnet-20241022     |
    Then the response status code should be 200
    And the response "provider" field should be "anthropic"
    And the "response" field should not be empty

  Scenario: Invalid provider returns error
    When I send a POST request to "/chat" with:
      | field    | value               |
      | message  | Hello               |
      | provider | invalid_provider    |
    Then the response status code should be 400
    And the response should contain an error message about unsupported provider

  Scenario: Empty message returns validation error
    When I send a POST request to "/chat" with:
      | field    | value   |
      | message  |         |
      | provider | ollama  |
    Then the response status code should be 422
    And the response should contain validation error details

  Scenario: Provider switching without changing API calls
    Given multiple providers are available
    When I send identical messages to different providers:
      | provider   | message                  |
      | ollama     | What is machine learning |
      | openai     | What is machine learning |
      | anthropic  | What is machine learning |
    Then all responses should have status code 200
    And all responses should contain a "response" field
    And each response should indicate the correct provider used

  Scenario: Health check shows provider availability
    Given Ollama is running
    And OpenAI API key is not configured
    And Anthropic API key is not configured
    When I send a GET request to "/health"
    Then the response status code should be 200
    And the "providers.ollama" field should be true
    And the "providers.openai" field should be false
    And the "providers.anthropic" field should be false

  Scenario: Custom model parameters are respected
    Given Ollama is running and available
    When I send a POST request to "/chat" with:
      | field      | value                    |
      | message    | Write a haiku            |
      | provider   | ollama                   |
      | parameters | {"temperature": 0.9}     |
    Then the response status code should be 200
    And the response should contain a creative response

  Scenario: Service handles provider unavailability gracefully
    Given Ollama is not running
    When I send a POST request to "/chat" with:
      | field    | value     |
      | message  | Hello     |
      | provider | ollama    |
    Then the response status code should be 500
    And the response should contain an error message about provider connectivity

  Scenario: Root endpoint provides API information
    When I send a GET request to "/"
    Then the response status code should be 200
    And the response should contain "name" field
    And the response should contain "endpoints" field
    And the "endpoints" field should describe available API routes
