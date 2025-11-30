# Databricks Mount to Azure Blob Storage
resource "databricks_secret_scope" "azure" {
  name = "azure-secrets"
}

resource "databricks_secret" "storage_account" {
  key          = "storage-account"
  string_value = azurerm_storage_account.storage.name
  scope        = databricks_secret_scope.azure.name
}

resource "databricks_secret" "storage_key" {
  key          = "storage-key"
  string_value = azurerm_storage_account.storage.primary_access_key
  scope        = databricks_secret_scope.azure.name
}

resource "databricks_mount" "azure_blob" {
  name = "azure-blob-mount"
  uri  = "wasbs://${azurerm_storage_container.container.name}@${azurerm_storage_account.storage.name}.blob.core.windows.net"

  extra_configs = {
    "fs.azure.account.key.${azurerm_storage_account.storage.name}.blob.core.windows.net" = "{{secrets/azure-secrets/storage-key}}"
  }
}