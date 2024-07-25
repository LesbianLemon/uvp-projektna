import csv
import os

from typing import Callable, Iterable, Literal
from io import TextIOWrapper


# hack: inherit from string to allow using this class instead of path represented as string
class Directory(str):
	def __new__(cls, dir_path: str=".") -> "Directory": # have to use "Directory" since cannot used class inside its definition
		"""
		Directory constructor.

		Parameters
		----------
		dir_path : str, default="."
			| a path to a valid directory

		Raises
		------
		ValueError
			| when `dir_path` is not a valid directory path
		"""

		if os.path.isdir(dir_path):
			return super().__new__(cls, dir_path)
		else:
			raise ValueError(f"Supplied directory path `{dir_path}` is not a valid directory.")


	def listdir(self) -> list[str]:
		"""
		Gets a list of everything in the directory and returns it as a list of strings.

		Returns
		-------
		list[str]
			| list of files and subdirectories in the directory
		"""

		return os.listdir(self)


	def listfiles(self) -> list[str]:
		"""
		Gets a list of only the files in the directory and returns it as a list of strings.

		Returns
		-------
			| list of files in the directory
		"""

		return list(filter(os.path.isfile, self.listdir()))


	def clear(self, paths: list[str]) -> None:
		"""
		Deletes those entires in `paths` that exist.

		Parameters
		----------
		paths : list[str]
			| list of paths to items to be deleted
		"""

		path: str
		for path in paths:
			if os.path.exists(path):
				os.remove(path)


	def cleardir(self) -> None:
		"""
		Deletes everything in the directory.
		"""

		self.clear([os.path.join(self, path) for path in self.listdir()])


	def clearfiles(self) -> None:
		"""
		Deletes all the files in the directory.
		"""

		self.clear([os.path.join(self, path) for path in self.listfiles()])


class File:
	dir: Directory
	filename: str

	_path: str

	def __init__(self, dir: Directory, filename: str) -> None:
		"""
		File initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file
		"""

		self.dir = dir
		self.filename = filename

		self._path = os.path.join(dir, filename)


	def __str__(self) -> str:
		return f"<File path={self._path}>"


	def exists(self) -> bool:
		"""
		Checks if the file the instance is representing exists.

		Returns
		-------
		bool
			| `True` if it exists otherwise `False`
		"""

		return os.path.exists(self._path)

	
	def write(self, writer: Callable[[TextIOWrapper], None], force: bool=False) -> Literal[0, 1, 2]:
		"""
		Tries writing to file using `writer`.
		Does not over-write files unless `force` is set to `True` and removes the file if an error occured while writing.

		Parameters
		----------
		writer : Callable[[TextIOWrapper], None]
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written
		force : bool, default=`False`
			| whether to force over-writing the file

		Returns
		-------
		Literal[0, 1, 2]
			| `0` if writing failed, `1` if file already exists and `force` is `False` and `2` if write was successful
		"""

		if self.exists() and not force:
			return 1

		try:
			with open(self._path, "w", encoding="utf-8") as file:
				writer(file)
				return 2
	
		except Exception as err:
			if os.path.exists(self._path):
				os.remove(self._path)

			print(f"{self} could not successfuly write to '{self._path}': {err}")
			return 0


	def read(self) -> str:
		"""
		Reads the whole file contents and returns in string format.

		Returns
		-------
		str
			| content of whole file
		"""

		with open(self._path, "r", encoding="utf-8") as file:
			return file.read()


	def remove(self) -> None:
		"""
		Delete the file.
		"""

		if self.exists():
			os.remove(self._path)


class HTMLFile(File):
	def __init__(self, dir: Directory, filename: str) -> None:
		"""
		HTMLFile initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file without '.html'
		"""

		super().__init__(dir, filename + ".html")
		
	
	def __str__(self) -> str:
		return f"<HTMLFile path={self._path}>"


	def write_html(
		self,
		html: str,
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> Literal[0, 1, 2]: # break arguments into seperate lines to avoid line being to long
		"""
		Write the given HTML to the file.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `html` is ignored and only `writer` is executed.

		Parameters
		----------
		html : str
			| HTML code to write
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		if not writer:
			def writer(file: TextIOWrapper) -> None:
				file.write(html)

		return self.write(writer, force=force)


class CSVFile(File):
	def __init__(self, dir: Directory, filename: str) -> None:
		""""
		CSVFile initialiser.

		Parameters
		----------
		dir : Directory
			| a Directory type representing where the file will be stored
		filename : str
			| name of the file without '.csv'
		"""

		super().__init__(dir, filename + ".csv")

	
	def __str__(self) -> str:
		return f"<CSVFile path={self._path}>"


	def write_rows(
		self,
		rows: Iterable[Iterable[str]],
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> Literal[0, 1, 2]: # break arguments into seperate lines to avoid line being to long
		"""
		Write given rows to CSV file.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `rows` is ignored and only `writer` is executed.

		Parameters
		----------
		rows : Iterable[Iterable[str]]
			| an iterable containing rows to be written, represented as iterables of strings
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		if not writer:
			def writer(file: TextIOWrapper) -> None:
				csv_writer = csv.writer(file) # typing skipped due to weird csv._writer type being inaccessible
				csv_writer.writerows(rows)

		return self.write(writer, force=force)


	def write_columns(
		self,
		columns: Iterable[Iterable[str]],
		force: bool=False,
		writer: Callable[[TextIOWrapper], None] | None=None
	) -> Literal[0, 1, 2]: # break arguments into seperate lines to avoid line being to long
		"""
		Write given columns to CSV file.
		If columns do not hold the same amount of values, will write smallest length column values per column.
		Does not over-write unless `force` is set to `True`.
		If a custom `writer` is supplied, `rows` is ignored and only `writer` is executed.

		Parameters
		----------
		columns : Iterable[Iterable[str]]
			| an iterable containing columns to be written, represented as iterables of strings
		force : bool, default=`False`
			| whether to force over-writing the file
		writer : Callable[[TextIOWrapper], None], optional
			| a callable object to be executed when file is opened, takes one parameter (TextIOWrapper) representing the file to be written 
		"""

		rows: Iterable[Iterable[str]] = zip(*columns) # columns to rows iterable
		return self.write_rows(rows, force=force, writer=writer)
