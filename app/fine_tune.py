"""LoRA fine‑tune of SentenceTransformer encoder."""
import torch, pandas as pd
from torch.utils.data import DataLoader
from sentence_transformers import SentenceTransformer, losses
from peft import LoraConfig, get_peft_model
from .config import DATA_PROC, EMBED_MODEL, LORA_OUTPUT


def main():
    if LORA_OUTPUT.exists():
        print("Adapter exists");
        return
    model = SentenceTransformer(EMBED_MODEL, device='cuda' if torch.cuda.is_available() else 'cpu')
    model.auto_model = get_peft_model(model.auto_model,
                                      LoraConfig(target_modules=['dense'], r=8, lora_alpha=16, lora_dropout=0.05))
    trip = pd.read_parquet(DATA_PROC / 'triplets.parquet')
    loader = DataLoader(list(zip(trip.query, trip.pos, trip.neg)), batch_size=32, shuffle=True)
    loss = losses.TripletLoss(model)
    model.fit(train_objectives=[(loader, loss)], epochs=1, warmup_steps=100)
    model.save(str(LORA_OUTPUT))


if __name__ == '__main__':
    main()
