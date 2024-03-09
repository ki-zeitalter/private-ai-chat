import {Component, CUSTOM_ELEMENTS_SCHEMA, Inject} from '@angular/core';
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

import 'deep-chat'
import {ChatService} from "../../services/chat.service";
import {BaseChatComponent} from "../base-chat/base-chat.component";
import {MatIcon} from "@angular/material/icon";
import {MatButtonModule, MatMiniFabButton} from "@angular/material/button";
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogTitle
} from "@angular/material/dialog";
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatInputModule} from "@angular/material/input";
import {FormsModule} from "@angular/forms";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatButtonToggle, MatButtonToggleGroup} from "@angular/material/button-toggle";
import {RequestDetails} from "deep-chat/dist/types/interceptors";

@Component({
  selector: 'app-text-to-image',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
    CommonModule,
    MatIcon,
    MatMiniFabButton,
  ],
  templateUrl: './text-to-image.component.html',
  styleUrl: './text-to-image.component.scss'
})
export class TextToImageComponent extends BaseChatComponent {

  imageSettings: ImageSettings = new ImageSettings();

  constructor(private _chatService: ChatService, public dialog: MatDialog) {
    super(_chatService)
  }

  protected override requestInterceptor(requestDetails: RequestDetails): RequestDetails {
    requestDetails = super.requestInterceptor(requestDetails);

    // Add the image settings to the request body
    requestDetails.body = {
      ...requestDetails.body,
      imageSettings: this.imageSettings
    }
    return requestDetails;
  }

  openSettingDialog(): void {
    const dialogRef = this.dialog.open(SettingsDialog, {
      data: this.imageSettings
    });

    dialogRef.afterClosed().subscribe(result => {
      this.imageSettings = result;
    });
  }

}

export class ImageSettings {
  size = "1024x1024";
  quality = "default";
  style = "vivid";
}

@Component({
  selector: 'text-to-image-settings-dialog',
  templateUrl: 'text-to-image-settings-dialog.html',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    FormsModule,
    MatButtonModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatSelect,
    MatOption,
    MatButtonToggleGroup,
    MatButtonToggle,
  ],
})
export class SettingsDialog {

  constructor(
    @Inject(MAT_DIALOG_DATA) public settings: ImageSettings
  ) {
  }


}
