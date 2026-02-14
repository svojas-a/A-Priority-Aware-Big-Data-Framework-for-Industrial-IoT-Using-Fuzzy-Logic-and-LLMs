from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model

# 1. Load dataset
dataset = load_dataset(
    "json",
    data_files={
        "train": "train.jsonl",
        "validation": "val.jsonl"
    }
)

# 2. Tokenizer
model_name = "mistralai/Mistral-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

def tokenize(example):
    text = (
        example["instruction"] + "\n\n"
        "Input:\n" + example["input"] + "\n\n"
        "Response:\n" + example["output"]
    )
    return tokenizer(text, truncation=True, padding="max_length", max_length=512)

dataset = dataset.map(tokenize, remove_columns=dataset["train"].column_names)

# 3. Load model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto"
)

# 4. Apply LoRA
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# 5. Training arguments
training_args = TrainingArguments(
    output_dir="./llm_fuzzy_model",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    evaluation_strategy="steps",
    save_steps=500,
    logging_steps=50,
    save_total_limit=2,
    report_to="none"
)

# 6. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"]
)

# 7. Train
trainer.train()

# 8. Save
model.save_pretrained("./llm_fuzzy_model")
tokenizer.save_pretrained("./llm_fuzzy_model")