

patch:
	git checkout master
	git pull
	poetry version patch
	git add pyproject.toml
	git commit -m "bumped version using patch"
	poetry install
	git tag $(slacksecrets version)
	git push
	git push --tags
	echo "Version bumped."

minor:
	git checkout master
	git pull
	poetry version minor
	git add pyproject.toml
	git commit -m "bumped version using major"
	poetry install
	git tag $(slacksecrets version)
	git push
	git push --tags
	echo "Version bumped."

major:
	git checkout master
	git pull
	poetry version major
	git add pyproject.toml
	git commit -m "bumped version using major"
	poetry install
	git tag $(slacksecrets version)
	git push
	git push --tags
	echo "Version bumped."

publish:
	poetry publish --build -u knightofni -p $(PYPI_PASSWORD)
	echo "Published."
