GAME_DIR := src/oblique_strategy_games
ITCH_USER := reayd-falmouth
ITCH_GAME := oblique-strategy-games
BUILD_DIR=$(GAME_DIR)/build
ZIP_FILE=web.zip

.PHONY: build deploy clean

install:
	@poetry install --no-root

# Check-in code after formatting
checkin: ## Perform a check-in after formatting the code
    ifndef COMMIT_MESSAGE
		$(eval COMMIT_MESSAGE := $(shell bash -c 'read -e -p "Commit message: " var; echo $$var'))
    endif
	@git add --all; \
	  git commit -m "$(COMMIT_MESSAGE)"; \
	  git push

# Generate layer requirements file
requirements: ## Generate layer requirements file
	@echo "Generating requirements file..."
	@poetry export --without-hashes -f requirements.txt -o $(GAME_DIR)/requirements.txt

build:
	@echo "Building the game with pygbag..."
	@poetry run python -m pygbag --build $(GAME_DIR)

zip:
	@echo "Creating web.zip from build directory..."
	@cd $(BUILD_DIR) && zip -r ../$(ZIP_FILE) .

deploy: build zip
	@echo "Uploading web.zip to Itch.io..."
	@butler push $(GAME_DIR)/$(ZIP_FILE) $(ITCH_USER)/$(ITCH_GAME):html5 --userversion=$(shell date +%Y%m%d%H%M)

status:
	@butler status $(ITCH_USER)/$(ITCH_GAME):html5

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(GAME_DIR)/build $(GAME_DIR)/$(ZIP_FILE)

run:
	@echo "Running game..."
	@python -m src.oblique_strategy_games.main

black:
	@echo "Formatting with black..."
	@poetry run black .