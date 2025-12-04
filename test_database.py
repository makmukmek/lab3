import pytest
import tempfile
import os
import sqlite3
from database import DatabaseManager
from models import Artwork

class TestDatabaseAddition:
    
    def test_add_artwork_to_database(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            test_artwork = Artwork(
                id=None,
                title="Звездная ночь",
                artist="Винсент Ван Гог",
                year=1889,
                style="Постимпрессионизм",
                price=100000000.0,
                created_at=""
            )
            
            artwork_id = db.add_artwork(test_artwork)
            
            assert artwork_id is not None
            assert artwork_id > 0
            
            artworks = db.get_all_artworks()
            assert len(artworks) == 1
            
            saved_artwork = artworks[0]
            assert saved_artwork.id == artwork_id
            assert saved_artwork.title == test_artwork.title
            assert saved_artwork.artist == test_artwork.artist
            assert saved_artwork.year == test_artwork.year
            assert saved_artwork.style == test_artwork.style
            assert saved_artwork.price == test_artwork.price
            assert saved_artwork.created_at is not None
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass

class TestDatabaseDeletion:
    
    def test_delete_existing_artwork(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            test_artwork = Artwork(
                id=None,
                title="Тестовое произведение",
                artist="Тестовый художник",
                year=2020,
                style="Тестовый стиль",
                price=1000.0,
                created_at=""
            )
            
            artwork_id = db.add_artwork(test_artwork)
            
            artworks_before = db.get_all_artworks()
            assert len(artworks_before) == 1
            
            db.delete_artwork(artwork_id)
            
            artworks_after = db.get_all_artworks()
            assert len(artworks_after) == 0
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_delete_non_existent_artwork(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            db.delete_artwork(999)
            
            artworks = db.get_all_artworks()
            assert len(artworks) == 0
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_delete_from_multiple_artworks(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            artworks_data = [
                ("Картина 1", "Художник 1", 2000, "Стиль 1", 1000.0),
                ("Картина 2", "Художник 2", 2001, "Стиль 2", 2000.0),
                ("Картина 3", "Художник 3", 2002, "Стиль 3", 3000.0),
            ]
            
            artwork_ids = []
            for title, artist, year, style, price in artworks_data:
                artwork = Artwork(
                    id=None,
                    title=title,
                    artist=artist,
                    year=year,
                    style=style,
                    price=price,
                    created_at=""
                )
                artwork_id = db.add_artwork(artwork)
                artwork_ids.append(artwork_id)
            
            artworks_before = db.get_all_artworks()
            assert len(artworks_before) == 3
            
            db.delete_artwork(artwork_ids[1])
            
            artworks_after = db.get_all_artworks()
            assert len(artworks_after) == 2
            
            remaining_titles = [artwork.title for artwork in artworks_after]
            assert "Картина 1" in remaining_titles
            assert "Картина 2" not in remaining_titles
            assert "Картина 3" in remaining_titles
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_database_integrity_after_deletion(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            test_artwork = Artwork(
                id=None,
                title="Тест целостности",
                artist="Тест художник",
                year=2020,
                style="Тест стиль",
                price=5000.0,
                created_at=""
            )
            
            artwork_id = db.add_artwork(test_artwork)
            
            db.delete_artwork(artwork_id)
            
            new_artwork = Artwork(
                id=None,
                title="Новое произведение",
                artist="Новый художник",
                year=2021,
                style="Новый стиль",
                price=6000.0,
                created_at=""
            )
            
            new_artwork_id = db.add_artwork(new_artwork)
            
            assert new_artwork_id > artwork_id
            
            artworks = db.get_all_artworks()
            assert len(artworks) == 1
            assert artworks[0].id == new_artwork_id
            assert artworks[0].title == "Новое произведение"
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass

class TestDatabaseEdgeCases:
    
    def test_delete_negative_id(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            db.delete_artwork(-1)
            
            artworks = db.get_all_artworks()
            assert len(artworks) == 0
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass
    
    def test_delete_zero_id(self):
        fd, db_path = tempfile.mkstemp(suffix='.db')
        try:
            os.close(fd)
            
            db = DatabaseManager(db_path)
            
            db.delete_artwork(0)
            
            artworks = db.get_all_artworks()
            assert len(artworks) == 0
            
        finally:
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except PermissionError:
                pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])