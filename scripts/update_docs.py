from l2m2.model_info import MODEL_INFO, HOSTED_PROVIDERS


header = "| Model Name | Provider(s) | Model Version(s) |\n"
sep = "| --- | --- | --- |\n"
rows = ""


def get_provider_link(provider_key):
    provider_name = HOSTED_PROVIDERS[provider_key]["name"]
    provider_homepage = HOSTED_PROVIDERS[provider_key]["homepage"]
    return f"[{provider_name}]({provider_homepage})"


def make_row(model_name):
    providers = []
    model_ids = []
    for provider_key, details in MODEL_INFO[model_name].items():
        providers.append(get_provider_link(provider_key))
        model_ids.append(f"`{details['model_id']}`")
    return f"| `{model_name}` | {', '.join(providers)} | {', '.join(model_ids)} |\n"


for model_name in MODEL_INFO:
    rows += make_row(model_name)

model_table = "\n\n" + header + sep + rows + "\n"


start_model_table = "<!--start-model-table-->"
end_model_table = "<!--end-model-table-->"


def replace_between(full_string, start, end, replacement):
    i_s = full_string.find(start)
    while i_s != -1:
        i_e = full_string.find(end, i_s)
        if i_e == -1:
            break
        full_string = (
            full_string[: i_s + len(start)] + str(replacement) + full_string[i_e:]  # type: ignore
        )
        i_s = full_string.find(start, i_e)
    return full_string


supported_models_path = "docs/supported_models.md"
with open(supported_models_path, "r") as f:
    out = f.read()
    out = replace_between(out, start_model_table, end_model_table, model_table)
with open(supported_models_path, "w") as f:
    f.write(out)
print("Updated supported_models.md")
