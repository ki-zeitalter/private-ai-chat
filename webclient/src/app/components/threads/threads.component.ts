import {Component, Inject, NgZone, OnInit} from '@angular/core';
import {MatListItem, MatNavList} from "@angular/material/list";
import {NgForOf, NgIf} from "@angular/common";
import {MessageContent} from "deep-chat/dist/types/messages";
import {Thread} from "../../model/thread.model";
import {ThreadsService} from "../../services/threads.service";
import {ChatService} from "../../services/chat.service";
import {Router} from "@angular/router";
import {MatIcon} from "@angular/material/icon";
import {MatButton, MatIconButton} from "@angular/material/button";
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogActions,
  MatDialogModule,
  MatDialogRef,
  MatDialogTitle
} from '@angular/material/dialog';

@Component({
  selector: 'app-threads',
  standalone: true,
  imports: [
    MatListItem,
    MatNavList,
    NgForOf,
    NgIf,
    MatIcon,
    MatIconButton
  ],
  templateUrl: './threads.component.html',
  styleUrl: './threads.component.scss'
})
export class ThreadsComponent implements OnInit {
  threads: Thread[] = []

  constructor(private ngZone: NgZone,
              private threadsService: ThreadsService,
              private chatService: ChatService,
              private router: Router,
              public dialog: MatDialog) {
  }

  ngOnInit() {
    this.newThread();

    this.loadThreads();


    this.chatService.onNewMessage.subscribe(() => {
      this.ngZone.run(() =>
        window.setTimeout(() => this.loadThreads(), 2000)
      )
    });
  }


  newThread(initialMessages?: MessageContent[]): void {
    this.router.navigate(['chat']).then(() => {
      this.chatService.activateThread(null)
    })
  }

  loadThreads() {
    this.threadsService.loadThreads(this.chatService.userId).subscribe(history => {
      console.log('Threads loaded', history)
      this.threads = history;
    })
  }

  activateThread(thread: Thread) {
    let target = 'chat'

    if (thread.app_type) {
      target = thread.app_type;
    }


    this.router.navigate([target]).then(() => {
      this.chatService.activateThread(thread);
    })

  }

  openDialog(thread_id: string): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      width: '450px',
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.threadsService.deleteThread(thread_id).subscribe(() => {
          this.loadThreads();
        })
      }
    });
  }
}

@Component({
  selector: 'app-confirmation-dialog',
  template: `
      <h1 mat-dialog-title>Are you sure you want to delete this thread?</h1>
      <div mat-dialog-actions>
          <button mat-button (click)="onNoClick()">No</button>
          <button mat-button [mat-dialog-close]="true" cdkFocusInitial>Yes</button>
      </div>
  `,
  imports: [
    MatDialogTitle,
    MatDialogActions,
    MatButton,
    MatDialogModule

  ],
  standalone: true
})
export class ConfirmationDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ConfirmationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any) {
  }

  onNoClick(): void {
    this.dialogRef.close();
  }
}
