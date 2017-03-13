from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from .cache import cache
from .log import logger


class VersionMatrixWorksheet:
    def __init__(self, json_key_file: str, sheet_key: str):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scope)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(sheet_key)
        self.worksheet = sheet.get_worksheet(0)

    @cache
    def get_row(self, row, min_col=2):
        return [cell for cell in self.worksheet.range(row, 1, row, self.worksheet.col_count) if cell.col >= min_col]

    @cache
    def get_column(self, col, min_row=2):
        return [cell for cell in self.worksheet.range(1, col, self.worksheet.row_count, col) if cell.row >= min_row]

    def find_or_create_column_header(self, value, updated_cells):
        cells = self.get_row(1)

        # find existing
        for cell in cells:
            if cell.value == value:
                return cell

        # find empty
        for cell in cells:
            if not cell.value:
                cell.value = value
                updated_cells.append(cell)
                return cell

        # create new
        if cells:
            col_number = max(cell.col for cell in cells if cell.value) + 1
        else:
            col_number = 2
        cell = self.worksheet.cell(1, col_number)
        cell.value = value
        updated_cells.append(cell)
        return cell

    def find_or_create_row_header(self, value, updated_cells):
        cells = self.get_column(1)

        # find existing
        for cell in cells:
            if cell.value == value:
                return cell

        # find empty
        for cell in cells:
            if not cell.value:
                cell.value = value
                updated_cells.append(cell)
                return cell

        # create new
        if cells:
            row_number = max(cell.row for cell in cells if cell.value) + 1
        else:
            row_number = 2
        cell = self.worksheet.cell(row_number, 1)
        cell.value = value
        updated_cells.append(cell)
        return cell

    def set_dependencies(self, repo, dependencies):
        updated_cells = []

        column_header = self.find_or_create_column_header(repo.name, updated_cells)
        logger.info("Updating %s in column #%s", column_header.value, column_header.col)

        version_column = {cell.row: cell for cell in self.get_column(column_header.col)}
        checked_rows = set()

        # check rows that have a dependency
        for dependency, version in dependencies.items():
            row_header = self.find_or_create_row_header(dependency, updated_cells)
            checked_rows.add(row_header.row)

            if row_header.row in version_column:
                cell = version_column[row_header.row]
            else:
                cell = self.worksheet.cell(row_header.row, column_header.col)
                version_column[row_header.row] = cell

            if cell.value != version:
                logger.info("Update dependency %s from \"%s\" to \"%s\"", dependency, cell.value, version)
                cell.value = version
                updated_cells.append(cell)

        # clear rows that do not have a dependency
        for cell in version_column.values():
            if cell.row not in checked_rows:
                if cell.value != "":
                    cell.value = ""
                    updated_cells.append(cell)

        if updated_cells:
            logger.info("Persisting %s cells", len(updated_cells))
            self.worksheet.update_cells(updated_cells)

    def set_updating(self):
        cell = self.worksheet.cell(1, 1)
        cell.value = "UPDATING"
        self.worksheet.update_cells([cell])

    def unset_updating(self):
        cell = self.worksheet.cell(1, 1)
        cell.value = datetime.now()
        self.worksheet.update_cells([cell])
