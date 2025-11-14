"""
Database module for sample project
"""
from typing import List, Dict, Optional, Any
import json


class Database:
    """Simple in-memory database"""

    def __init__(self):
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        self.indexes: Dict[str, Dict[str, int]] = {}

    def create_table(self, table_name: str) -> bool:
        """Create a new table"""
        if table_name in self.tables:
            return False
        self.tables[table_name] = []
        self.indexes[table_name] = {}
        return True

    def insert(self, table_name: str, record: Dict[str, Any]) -> bool:
        """Insert a record into table"""
        if table_name not in self.tables:
            return False

        if 'id' not in record:
            record['id'] = len(self.tables[table_name]) + 1

        self.tables[table_name].append(record)

        # Update index
        if 'id' in record:
            self.indexes[table_name][record['id']] = len(self.tables[table_name]) - 1

        return True

    def find_by_id(self, table_name: str, record_id: Any) -> Optional[Dict[str, Any]]:
        """Find record by ID"""
        if table_name not in self.tables:
            return None

        if record_id in self.indexes[table_name]:
            idx = self.indexes[table_name][record_id]
            return self.tables[table_name][idx]

        return None

    def find_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all records from table"""
        if table_name not in self.tables:
            return []
        return self.tables[table_name].copy()

    def update(self, table_name: str, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Update a record"""
        if table_name not in self.tables:
            return False

        if record_id not in self.indexes[table_name]:
            return False

        idx = self.indexes[table_name][record_id]
        self.tables[table_name][idx].update(updates)
        return True

    def delete(self, table_name: str, record_id: Any) -> bool:
        """Delete a record"""
        if table_name not in self.tables:
            return False

        if record_id not in self.indexes[table_name]:
            return False

        idx = self.indexes[table_name][record_id]
        del self.tables[table_name][idx]

        # Rebuild index
        self.indexes[table_name] = {}
        for i, record in enumerate(self.tables[table_name]):
            if 'id' in record:
                self.indexes[table_name][record['id']] = i

        return True

    def query(self, table_name: str, filter_func) -> List[Dict[str, Any]]:
        """Query records with custom filter"""
        if table_name not in self.tables:
            return []

        return [record for record in self.tables[table_name] if filter_func(record)]

    def count(self, table_name: str) -> int:
        """Count records in table"""
        if table_name not in self.tables:
            return 0
        return len(self.tables[table_name])

    def export_to_json(self, table_name: str) -> str:
        """Export table to JSON"""
        if table_name not in self.tables:
            return "[]"
        return json.dumps(self.tables[table_name], indent=2)

    def import_from_json(self, table_name: str, json_data: str) -> bool:
        """Import table from JSON"""
        try:
            data = json.loads(json_data)
            if not isinstance(data, list):
                return False

            if table_name not in self.tables:
                self.create_table(table_name)

            self.tables[table_name] = data

            # Rebuild indexes
            self.indexes[table_name] = {}
            for i, record in enumerate(data):
                if 'id' in record:
                    self.indexes[table_name][record['id']] = i

            return True
        except (json.JSONDecodeError, Exception):
            return False
