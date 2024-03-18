import {Component} from '@angular/core';
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatSlideToggle} from "@angular/material/slide-toggle";
import {MatDivider} from "@angular/material/divider";
import {MatIcon} from "@angular/material/icon";
import {MatMiniFabButton} from "@angular/material/button";
import {RouterLink} from "@angular/router";
import {MatList, MatListItem, MatListOption, MatSelectionList} from "@angular/material/list";
import {AICard} from "../../model/ai-card.model";

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
    MatListOption
  ],
  templateUrl: './assistant-editor.component.html',
  styleUrl: './assistant-editor.component.scss'
})
export class AssistantEditorComponent {
  assistantData: AICard = {
    name: '',
    description: '',
    type: '',
    agent_id: '',
    creator: '',
    instructions: '',
    tools: []
  };
}
