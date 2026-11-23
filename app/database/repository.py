
from sqlalchemy.orm import Session

from app.database.models import Dataset


def save_dataset(db: Session, dataset_data: dict):

    dataset = Dataset(**dataset_data)

    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return dataset


def get_dataset(db: Session, dataset_id: str):

    return db.query(Dataset).filter(
        Dataset.dataset_id == dataset_id
    ).first()


def get_all_datasets(db: Session):

    return db.query(Dataset).order_by(
        Dataset.upload_date.desc()
    ).all()

def delete_dataset(db: Session, dataset_id: str):

    dataset = get_dataset(db, dataset_id)

    if not dataset:
        return None

    db.delete(dataset)
    db.commit()

    return dataset