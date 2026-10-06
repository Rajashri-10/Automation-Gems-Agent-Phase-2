from pathlib import Path


class AgentCreator:

    def __init__(
        self,
        page,
        dry_run: bool = True,
    ):
        self.page = page
        self.dry_run = dry_run

    def dismiss_any_dialogs(self):
        """Dismisses any blocking popups such as 'Keep or discard this agent?', welcome dialogs, etc."""
        for label in ["Keep Draft", "Discard and Leave", "Keep draft", "Discard", "Get started", "Continue editing"]:
            try:
                btn = self.page.locator("button, [role='button'], ucs-confirmation-dialog button").filter(has_text=label).first
                if not btn.is_visible(timeout=300):
                    btn = self.page.get_by_text(label, exact=False).first
                if btn.is_visible(timeout=300):
                    btn.click(force=True)
                    self.page.wait_for_timeout(500)
            except Exception:
                pass

    def open_agent_builder(
        self,
    ):
        self.page.wait_for_timeout(2000)
        self.dismiss_any_dialogs()

        sidebar_btn = self.page.get_by_label("Open sidebar")
        try:
            if sidebar_btn.is_visible(timeout=1000):
                sidebar_btn.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

        self.dismiss_any_dialogs()

        new_agent_btn = self.page.get_by_label(
            "New agent",
            exact=True,
        )
        if not new_agent_btn.is_visible(timeout=3000):
            new_agent_btn = self.page.get_by_role("button", name="New agent")
            
        new_agent_btn.wait_for(state="visible", timeout=5000)
        new_agent_btn.click()
        self.page.wait_for_timeout(1000)

        # Handle Chat agent menu item with retry if menu didn't open
        chat_menu_item = self.page.get_by_role("menuitem", name="Chat agent")
        if not chat_menu_item.is_visible(timeout=3000):
            new_agent_btn.click()
            self.page.wait_for_timeout(1000)
            
        chat_menu_item.click(timeout=5000)
        self.page.wait_for_timeout(1500)

        # Click Build manually button
        build_manually = self.page.get_by_role("button", name="Build manually")
        if not build_manually.is_visible(timeout=3000):
            build_manually = self.page.get_by_text("Build manually", exact=False)
            
        build_manually.wait_for(state="visible", timeout=10000)
        build_manually.click(force=True)
        self.page.wait_for_timeout(2500)

        # Click the central node to open the details side panel
        central_node = self.page.get_by_text("Agent to help interact with enterprise data.", exact=False)
        central_node.wait_for(state="visible", timeout=20000)
        central_node.click(force=True)
        self.page.wait_for_timeout(1000)

    def fill_agent(
        self,
        record: dict,
    ):
        name = record["name"]
        description = record["description"]
        instructions = record["instructions"]

        # Ensure Details side panel is open
        name_field = self.page.get_by_label("Name", exact=False).first
        if not name_field.is_visible(timeout=2000):
            try:
                self.page.get_by_text("Agent to help interact with enterprise data.", exact=False).click(force=True)
                self.page.wait_for_timeout(1000)
            except Exception:
                pass
        name_field = self.page.get_by_label("Name", exact=False).first
        description_field = self.page.get_by_label("Description", exact=False).first
        
        instructions_field = self.page.get_by_label("Instructions", exact=False).locator("textarea, [contenteditable]").first
        if not instructions_field.is_visible(timeout=1000):
            instructions_field = self.page.get_by_label("Instructions", exact=False).first

        # Truncate strings to prevent backend INVALID_ARGUMENT limits
        if len(instructions) > 500:
            print(f"Truncating instructions from {len(instructions)} to 500 characters to prevent backend INVALID_ARGUMENT")
            instructions = instructions[:500]
            
        if len(description) > 100:
            print(f"Truncating description from {len(description)} to 100 characters to prevent backend INVALID_ARGUMENT")
            description = description[:100]
            
        if len(name) > 30:
            print(f"Truncating name from {len(name)} to 30 characters to prevent backend INVALID_ARGUMENT")
            name = name[:30]

        for field, text in [(name_field, name), (description_field, description), (instructions_field, instructions)]:
            field.click()
            self.page.wait_for_timeout(200)
            
            # Clear existing text
            modifier = "Meta"
            self.page.keyboard.press(f"{modifier}+A")
            self.page.keyboard.press("Backspace")
            self.page.wait_for_timeout(100)
            
            # Type text character by character (fast)
            self.page.keyboard.type(text)
            self.page.wait_for_timeout(200)
            field.press("Tab")
            self.page.wait_for_timeout(200)

        # Select supported model (3.6 Flash is enabled in backend WIZ config)
        try:
            model_dropdown = self.page.locator("mat-select, [role='combobox']").last
            if not model_dropdown.is_visible(timeout=1000):
                model_dropdown = self.page.get_by_text("3.8 Flash").last
            
            if model_dropdown.is_visible(timeout=1000):
                model_dropdown.scroll_into_view_if_needed()
                model_dropdown.click(timeout=3000)
                self.page.wait_for_timeout(600)
                
                # Look for 3.6 Flash in the dropdown menu
                option_36 = self.page.locator("mat-option, [role='option']").filter(has_text="3.6 Flash").first
                if not option_36.is_visible(timeout=1000):
                    option_36 = self.page.get_by_text("3.6 Flash", exact=False).first
                if option_36.is_visible(timeout=1000):
                    option_36.click(timeout=3000)
                    self.page.wait_for_timeout(600)
        except Exception as e:
            print(f"Model selection note: {e}")

        self.page.wait_for_timeout(500)

    def validate_form(self):
        name_field = self.page.get_by_label("Name", exact=False).first
        description_field = self.page.get_by_label("Description", exact=False).first
        
        instructions_field = self.page.get_by_label("Instructions", exact=False).locator("textarea, [contenteditable]").first
        if not instructions_field.is_visible(timeout=1000):
            instructions_field = self.page.get_by_label("Instructions", exact=False).first

        if not name_field.input_value().strip():
            raise ValueError("Name field is empty.")

        if not description_field.input_value().strip():
            raise ValueError("Description field is empty.")

        # For custom elements, input_value might fail so we use text_content as fallback
        inst_val = ""
        try:
            inst_val = instructions_field.input_value()
        except:
            inst_val = instructions_field.text_content()
            
        if not inst_val or not inst_val.strip():
            raise ValueError("Instructions field is empty.")

    def create_agent(self):

        if self.dry_run:
            print(
                "DRY_RUN=true "
                "- Create button will not be clicked."
            )
            return False

        # We need to make sure we click the main blue Create button at the top right
        create_button = self.page.get_by_role("button", name="Create", exact=True).last
        
        # Verify it is visible and click aggressively
        create_button.wait_for(state="visible")
        
        # ==========================================
        # NETWORK INTERCEPTION FOR DEBUGGING
        # ==========================================
        import json
        
        requests_data = []
        responses_data = []
        
        def handle_request(req):
            if "discoveryengine" in req.url or "vertexaisearch" in req.url or "Widget" in req.url:
                requests_data.append(req.url)
                with open("artifacts/create_request_debug.json", "w") as f:
                    json.dump(requests_data, f, indent=2)

        def handle_response(res):
            if "discoveryengine" in res.url or "vertexaisearch" in res.url or "Widget" in res.url:
                try:
                    body = res.text()
                except:
                    body = "<binary/unreadable>"
                responses_data.append({
                    "url": res.url,
                    "status": res.status,
                    "body": body
                })
                with open("artifacts/create_response_debug.json", "w") as f:
                    json.dump(responses_data, f, indent=2)

        self.page.on("request", handle_request)
        self.page.on("response", handle_response)
        # ==========================================
        
        create_button.click(force=True)
        self.page.wait_for_timeout(2000)

        return True

    def wait_for_creation_success(self):
        # Wait for the creation response
        self.page.wait_for_timeout(3000)
        
        # Check if error toast appeared
        error_toast = self.page.get_by_text("WidgetService.WidgetDeployLowCodeAgent", exact=False)
        if error_toast.is_visible():
            raise Exception("Backend rejected creation: " + error_toast.text_content())
            
        # Check for success modal if present
        try:
            success_modal = self.page.get_by_text("Agent Created Successfully", exact=False)
            if success_modal.is_visible(timeout=3000):
                print("Agent created successfully popup detected.")
        except Exception:
            pass
            
        return True

    def click_chat_with_agent(self):
        try:
            chat_btn = self.page.get_by_role("button", name="Chat with Agent")
            if not chat_btn.is_visible(timeout=2000):
                chat_btn = self.page.get_by_text("Chat with Agent", exact=True)
                
            if chat_btn.is_visible(timeout=2000):
                chat_btn.click()
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(3000)
            else:
                cont_btn = self.page.get_by_text("Continue editing", exact=True)
                if cont_btn.is_visible(timeout=1000):
                    cont_btn.click()
                    self.page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Post-creation dialog interaction note: {e}")

    def return_to_agents_page(self):
        # Navigate back to the Agents page
        try:
            agents_nav = self.page.get_by_text("Agents", exact=True).first
            if agents_nav.is_visible(timeout=2000):
                agents_nav.click()
            else:
                self.page.go_back()
        except Exception:
            self.page.go_back()
            
        self.page.wait_for_timeout(1500)
        self.dismiss_any_dialogs()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        
    def verify_agents_page(self):
        self.dismiss_any_dialogs()
        new_agent_btn = self.page.get_by_label("New agent", exact=True)
        if not new_agent_btn.is_visible(timeout=5000):
            new_agent_btn = self.page.get_by_role("button", name="New agent")
            new_agent_btn.wait_for(state="visible", timeout=5000)
        return True