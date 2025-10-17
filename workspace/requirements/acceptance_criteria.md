# Acceptance Criteria (Gherkin-style)

Feature: Project management
  Scenario: Create project
    Given I am on the New Project page
    When I enter a name and optional description and submit
    Then I see the project detail page with empty To Do/In Progress/Done columns

  Scenario: Archive project
    Given I am viewing an active project
    When I click Archive and confirm
    Then the project appears under Archived Projects and is removed from Active

Feature: Task creation and editing
  Scenario: Quick add task
    Given I am on a project detail page
    When I click Add Task in To Do and enter a title
    Then the task appears in To Do with default priority Medium and is editable

  Scenario: Edit task inline
    Given a task exists
    When I click its title and change it
    Then the updated title is saved without full page reload

Feature: Drag-and-drop status updates
  Scenario: Move to In Progress with undo
    Given a task in To Do
    When I drag it to In Progress
    Then the task status updates immediately and I see a toast with an Undo option

  Scenario: Undo move
    Given I just moved a task
    When I click Undo within 10 seconds
    Then the task returns to its previous status and position

Feature: Move tasks between projects
  Scenario: Move task to another project
    Given a task in Project A
    When I choose Move to Project and select Project B
    Then the task appears in Project B with all fields intact

Feature: Progress tracking
  Scenario: Project completion percentage
    Given a project with 5 tasks, 1 done
    When I view the project header
    Then I see 20% complete and 1 of 5 tasks done

  Scenario: Overdue highlighting
    Given a task with due date in the past and status not Done
    When I view the board
    Then the task is highlighted as overdue

Feature: Data export
  Scenario: Export project to CSV
    Given I am on a project
    When I click Export CSV
    Then I download a CSV with project tasks and metadata

Feature: Backups
  Scenario: Daily snapshot
    Given the scheduler runs daily
    When the backup command executes
    Then a snapshot file is created and retained per policy
