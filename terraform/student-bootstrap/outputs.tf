output "students" {
  description = "Single-element list shaped to match the reference track's setup-workstation script."
  value = [
    {
      project_key = launchdarkly_project.student.key
    }
  ]
}
