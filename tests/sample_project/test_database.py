"""
Tests for database module
"""
import pytest
import json
from .database import Database


class TestDatabase:
    """Test cases for Database"""

    @pytest.fixture
    def db(self):
        """Create database fixture"""
        return Database()

    def test_create_table_success(self, db):
        """Test successful table creation"""
        result = db.create_table('users')
        assert result is True
        assert 'users' in db.tables

    def test_create_table_duplicate(self, db):
        """Test creating duplicate table"""
        db.create_table('users')
        result = db.create_table('users')
        assert result is False

    def test_insert_record(self, db):
        """Test inserting record"""
        db.create_table('users')
        record = {'name': 'John', 'age': 30}
        result = db.insert('users', record)
        assert result is True
        assert len(db.tables['users']) == 1

    def test_insert_auto_id(self, db):
        """Test auto ID generation"""
        db.create_table('users')
        record = {'name': 'John'}
        db.insert('users', record)
        assert 'id' in db.tables['users'][0]

    def test_insert_nonexistent_table(self, db):
        """Test inserting into non-existent table"""
        result = db.insert('users', {'name': 'John'})
        assert result is False

    def test_find_by_id_success(self, db):
        """Test finding record by ID"""
        db.create_table('users')
        record = {'id': 1, 'name': 'John'}
        db.insert('users', record)
        found = db.find_by_id('users', 1)
        assert found is not None
        assert found['name'] == 'John'

    def test_find_by_id_not_found(self, db):
        """Test finding non-existent record"""
        db.create_table('users')
        found = db.find_by_id('users', 999)
        assert found is None

    def test_find_by_id_nonexistent_table(self, db):
        """Test finding in non-existent table"""
        found = db.find_by_id('users', 1)
        assert found is None

    def test_find_all(self, db):
        """Test finding all records"""
        db.create_table('users')
        db.insert('users', {'name': 'John'})
        db.insert('users', {'name': 'Jane'})
        records = db.find_all('users')
        assert len(records) == 2

    def test_find_all_empty(self, db):
        """Test finding all in empty table"""
        db.create_table('users')
        records = db.find_all('users')
        assert len(records) == 0

    def test_find_all_nonexistent_table(self, db):
        """Test finding all in non-existent table"""
        records = db.find_all('users')
        assert len(records) == 0

    def test_update_record(self, db):
        """Test updating record"""
        db.create_table('users')
        db.insert('users', {'id': 1, 'name': 'John', 'age': 30})
        result = db.update('users', 1, {'age': 31})
        assert result is True

        record = db.find_by_id('users', 1)
        assert record['age'] == 31

    def test_update_nonexistent_record(self, db):
        """Test updating non-existent record"""
        db.create_table('users')
        result = db.update('users', 999, {'age': 31})
        assert result is False

    def test_update_nonexistent_table(self, db):
        """Test updating in non-existent table"""
        result = db.update('users', 1, {'age': 31})
        assert result is False

    def test_delete_record(self, db):
        """Test deleting record"""
        db.create_table('users')
        db.insert('users', {'id': 1, 'name': 'John'})
        result = db.delete('users', 1)
        assert result is True
        assert len(db.tables['users']) == 0

    def test_delete_nonexistent_record(self, db):
        """Test deleting non-existent record"""
        db.create_table('users')
        result = db.delete('users', 999)
        assert result is False

    def test_delete_nonexistent_table(self, db):
        """Test deleting from non-existent table"""
        result = db.delete('users', 1)
        assert result is False

    def test_query_with_filter(self, db):
        """Test querying with filter"""
        db.create_table('users')
        db.insert('users', {'name': 'John', 'age': 30})
        db.insert('users', {'name': 'Jane', 'age': 25})
        db.insert('users', {'name': 'Bob', 'age': 35})

        results = db.query('users', lambda r: r['age'] > 28)
        assert len(results) == 2

    def test_query_nonexistent_table(self, db):
        """Test querying non-existent table"""
        results = db.query('users', lambda r: r['age'] > 28)
        assert len(results) == 0

    def test_count(self, db):
        """Test counting records"""
        db.create_table('users')
        db.insert('users', {'name': 'John'})
        db.insert('users', {'name': 'Jane'})
        count = db.count('users')
        assert count == 2

    def test_count_empty(self, db):
        """Test counting empty table"""
        db.create_table('users')
        count = db.count('users')
        assert count == 0

    def test_count_nonexistent_table(self, db):
        """Test counting non-existent table"""
        count = db.count('users')
        assert count == 0

    def test_export_to_json(self, db):
        """Test exporting table to JSON"""
        db.create_table('users')
        db.insert('users', {'id': 1, 'name': 'John'})
        json_data = db.export_to_json('users')
        data = json.loads(json_data)
        assert len(data) == 1
        assert data[0]['name'] == 'John'

    def test_export_nonexistent_table(self, db):
        """Test exporting non-existent table"""
        json_data = db.export_to_json('users')
        assert json_data == "[]"

    def test_import_from_json(self, db):
        """Test importing table from JSON"""
        json_data = json.dumps([
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'}
        ])
        result = db.import_from_json('users', json_data)
        assert result is True
        assert db.count('users') == 2

    def test_import_invalid_json(self, db):
        """Test importing invalid JSON"""
        result = db.import_from_json('users', 'invalid json')
        assert result is False

    def test_import_non_list_json(self, db):
        """Test importing non-list JSON"""
        json_data = json.dumps({'name': 'John'})
        result = db.import_from_json('users', json_data)
        assert result is False
