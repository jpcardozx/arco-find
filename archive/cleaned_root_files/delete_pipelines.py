import os

project_root = "C:\Users\João Pedro Cardozo\projetos\arco-find"

files_to_delete = [
    os.path.join(project_root, "pipelines", "advanced_pipeline.py"),
    os.path.join(project_root, "core", "complete_pipeline.py"),
    os.path.join(project_root, "core", "pipeline.py"),
    os.path.join(project_root, "legacy", "root_cleanup", "arco_realistic_financial_pipeline.py"),
    os.path.join(project_root, "legacy", "root_cleanup", "arco_smart_pipeline.py"),
    os.path.join(project_root, "legacy", "root_cleanup", "arco_customer_acquisition_pipeline.py"),
    os.path.join(project_root, "legacy", "root_cleanup", "arco_pipeline_launcher.py"),
    os.path.join(project_root, "legacy", "root_cleanup", "qualification_pipeline.py"),
    os.path.join(project_root, "pipelines", "standard_pipeline.py"),
    os.path.join(project_root, "legacy", "arco_customer_acquisition_pipeline.py"),
    os.path.join(project_root, "legacy", "qualification_pipeline.py"),
    os.path.join(project_root, "pipeline", "realistic_pipeline.py"),
    os.path.join(project_root, "legacy", "arco_realistic_financial_pipeline.py"),
    os.path.join(project_root, "pipeline", "smart_pipeline.py"),
    os.path.join(project_root, "legacy", "arco_smart_pipeline.py"),
    os.path.join(project_root, "legacy", "deprecated_engines", "arco_customer_acquisition_pipeline.py"),
    os.path.join(project_root, "legacy", "arco_pipeline_launcher.py"),
    os.path.join(project_root, "archive", "qualification_pipeline.py"),
    os.path.join(project_root, "archive", "arco_pilot_pipeline_v21.py"),
    os.path.join(project_root, "archive", "arco_pipeline_operational.py"),
    os.path.join(project_root, "archive", "arco_pipeline_real.py"),
    os.path.join(project_root, "archive", "engines", "intelligent_pipeline.py"),
    os.path.join(project_root, "archive", "real_engine", "enhanced_pipeline.py"),
    os.path.join(project_root, "archive", "scrapy_engine", "pipeline_optimizer.py"),
    os.path.join(project_root, "archive", "scrapy_engine", "pipelines.py"),
    os.path.join(project_root, "tests", "test_enhanced_pipeline.py")
]

for file_path in files_to_delete:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Excluído: {file_path}")
        except Exception as e:
            print(f"Erro ao excluir {file_path}: {e}")
    else:
        print(f"Arquivo não encontrado (já excluído ou caminho incorreto): {file_path}")

print("Processo de exclusão concluído.")
