import {Component} from '@angular/core';
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatSlideToggle} from "@angular/material/slide-toggle";
import {MatDivider} from "@angular/material/divider";
import {MatIcon} from "@angular/material/icon";
import {MatButton, MatMiniFabButton} from "@angular/material/button";
import {RouterLink} from "@angular/router";
import {MatList, MatListItem, MatListOption, MatSelectionList} from "@angular/material/list";
import {Assistant} from "../../model/assistant.model";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {NgForOf} from "@angular/common";
import {FormGroup, FormControl, Validators} from '@angular/forms';
import {v4 as uuidv4} from "uuid";
import {AssistantService} from "../../services/assistant.service";

@Component({
  selector: 'app-assistant-editor',
  standalone: true,
  imports: [
    MatFormField,
    MatInput,
    MatSelect,
    MatOption,
    MatLabel,
    MatSlideToggle,
    MatDivider,
    MatIcon,
    MatMiniFabButton,
    RouterLink,
    MatList,
    MatListItem,
    MatSelectionList,
    MatListOption,
    FormsModule,
    NgForOf,
    MatButton,
    ReactiveFormsModule
  ],
  templateUrl: './assistant-editor.component.html',
  styleUrl: './assistant-editor.component.scss'
})
export class AssistantEditorComponent {

  formular = new FormGroup({
    name: new FormControl('', Validators.required),
    instructions: new FormControl('', Validators.required),
    description: new FormControl('', Validators.required),
    model: new FormControl(''),
    codeInterpreter: new FormControl(false),
    retrieval: new FormControl(false),
    // TODO functions
  });

  constructor(private aiCardService: AssistantService) {
  }


  files: any[] = [];

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const base64String = reader.result?.toString().split(',')[1];
      this.files.push(base64String);
    };
    reader.readAsDataURL(file);
  }

  save(): void {
    const tools = [];

    if (this.formular.get('codeInterpreter')?.value) {
      tools.push('{"type": "code_interpreter"}');
    }
    if (this.formular.get('retrieval')?.value) {
      tools.push('{"type": "retrieval"}');
    }

    const assistantData: Assistant = {
      name: this.formular.get('name')!.value!,
      description: this.formular.get('description')!.value!,
      type: 'assistant',
      agent_id: uuidv4(),
      creator: 'manual',
      instructions: this.formular.get('instructions')!.value!,
      tools: tools,
      files: this.files
    };
    console.log(assistantData);

    this.aiCardService.saveAssistant(assistantData).subscribe(card => {
      console.log(card);
    });
  }
}
