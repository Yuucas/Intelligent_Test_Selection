"""
Analyzes git diffs to detect code changes
"""
import os
import subprocess
from typing import List, Dict, Set, Optional
from dataclasses import dataclass


@dataclass
class FileDiff:
    """Represents changes to a file"""
    file_path: str
    lines_added: int
    lines_removed: int
    lines_modified: int
    hunks: List[Dict]


class DiffAnalyzer:
    """Analyzes code diffs using git or direct comparison"""

    def __init__(self, repo_path: str = '.'):
        self.repo_path = repo_path

    def get_changed_files(self, commit: str = 'HEAD', base: str = 'HEAD~1') -> List[str]:
        """Get list of changed files between commits"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', base, commit],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                return [f for f in files if f.endswith('.py')]
            else:
                return []

        except (subprocess.SubprocessError, FileNotFoundError):
            # Git not available or not a git repo
            return []

    def get_uncommitted_changes(self) -> List[str]:
        """Get list of uncommitted changed files"""
        try:
            # Get both staged and unstaged changes
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            files = []
            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

            # Also get untracked files
            result = subprocess.run(
                ['git', 'ls-files', '--others', '--exclude-standard'],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            if result.returncode == 0:
                untracked = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                files.extend(untracked)

            return [f for f in files if f.endswith('.py')]

        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def analyze_diff(self, file_path: str, commit: str = 'HEAD', base: str = 'HEAD~1') -> Optional[FileDiff]:
        """Analyze diff for a specific file"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--unified=0', base, commit, '--', file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            if result.returncode != 0:
                return None

            return self._parse_diff(file_path, result.stdout)

        except (subprocess.SubprocessError, FileNotFoundError):
            return None

    def _parse_diff(self, file_path: str, diff_output: str) -> FileDiff:
        """Parse git diff output"""
        lines_added = 0
        lines_removed = 0
        hunks = []

        current_hunk = None

        for line in diff_output.split('\n'):
            if line.startswith('@@'):
                # New hunk
                if current_hunk:
                    hunks.append(current_hunk)

                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                parts = line.split('@@')[1].strip().split()
                current_hunk = {
                    'old_range': parts[0],
                    'new_range': parts[1] if len(parts) > 1 else '',
                    'changes': []
                }

            elif line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
                if current_hunk:
                    current_hunk['changes'].append(('add', line[1:]))

            elif line.startswith('-') and not line.startswith('---'):
                lines_removed += 1
                if current_hunk:
                    current_hunk['changes'].append(('remove', line[1:]))

        if current_hunk:
            hunks.append(current_hunk)

        return FileDiff(
            file_path=file_path,
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=min(lines_added, lines_removed),
            hunks=hunks
        )

    def get_change_magnitude(self, file_path: str) -> float:
        """Calculate change magnitude for a file (0.0 to 1.0)"""
        diff = self.analyze_diff(file_path)
        if not diff:
            return 0.0

        # Calculate magnitude based on lines changed
        total_changes = diff.lines_added + diff.lines_removed

        # Normalize to 0-1 scale (capped at 100 lines)
        magnitude = min(total_changes / 100.0, 1.0)

        return magnitude

    def get_changed_line_numbers(self, file_path: str) -> Set[int]:
        """Get set of changed line numbers"""
        diff = self.analyze_diff(file_path)
        if not diff:
            return set()

        changed_lines = set()

        for hunk in diff.hunks:
            # Parse new range: +start,count
            new_range = hunk['new_range']
            if new_range.startswith('+'):
                parts = new_range[1:].split(',')
                start = int(parts[0])
                count = int(parts[1]) if len(parts) > 1 else 1

                changed_lines.update(range(start, start + count))

        return changed_lines

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                cwd=self.repo_path
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
