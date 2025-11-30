terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "databricks-etl-rg"
  location = "East US"
}

# Azure Container Registry for Docker images
resource "azurerm_container_registry" "acr" {
  name                = "databricksetlacr"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# Create Storage Account
resource "azurerm_storage_account" "storage" {
  name                     = "databricksetlstorage"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "container" {
  name                  = "etl-data"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

# AKS Cluster for Airflow
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "etl-aks-cluster"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "etlaks"

  default_node_pool {
    name       = "default"
    node_count = 2
    vm_size    = "Standard_DS2_v2"
  }

  identity {
    type = "SystemAssigned"
  }
}

provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.aks.kube_config.0.host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.aks.kube_config.0.host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate)
  }
}

# Deploy Airflow using Helm
resource "helm_release" "airflow" {
  name       = "airflow"
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  version    = "1.10.0"

  values = [
    file("${path.module}/airflow-values.yaml")
  ]

  set {
    name  = "dags.gitSync.enabled"
    value = "true"
  }

  set {
    name  = "dags.gitSync.repo"
    value = "https://github.com/your-repo/dockerized-databricks-etl"
  }

  set {
    name  = "dags.gitSync.branch"
    value = "main"
  }
}

# Databricks Workspace
resource "azurerm_databricks_workspace" "workspace" {
  name                = "databricks-etl-workspace"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"
}

# Configure Databricks provider
provider "databricks" {
  host = azurerm_databricks_workspace.workspace.workspace_url
}

# Cluster
resource "databricks_cluster" "cluster" {
  cluster_name            = "etl-cluster"
  spark_version           = "13.3.x-scala2.12"
  node_type_id            = "Standard_DS3_v2"
  autotermination_minutes = 20
  num_workers             = 1
}

# Job
resource "databricks_job" "etl_job" {
  name = "wallet-activity-etl"

  task {
    task_key = "run_etl"

    new_cluster {
      spark_version = databricks_cluster.cluster.spark_version
      node_type_id  = databricks_cluster.cluster.node_type_id
      num_workers   = 1
    }

    python_wheel_task {
      package_name = "dockerized-databricks-etl"
      entry_point  = "main"
    }

    environment_key = databricks_environment.env.environment_key
  }

  schedule {
    quartz_cron_expression = "0 0 * * * ?"
    timezone_id            = "UTC"
  }
}

# Environment for the job
resource "databricks_environment" "env" {
  name = "etl-env"

  spec {
    dependencies = [
      "dockerized-databricks-etl"
    ]
  }
}
