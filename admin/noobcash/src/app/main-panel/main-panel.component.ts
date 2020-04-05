import { Component, OnInit } from '@angular/core';
import { filter, map } from 'rxjs/operators';
import { Node } from 'src/models/node';
import { Store } from '@ngrx/store';
import { AppState } from '../reducers';
import { Observable } from 'rxjs';
import { Error } from 'src/models/error';
import { KillSystem } from '../actions/system.actions';

import {MediaChange, MediaObserver} from '@angular/flex-layout';

@Component({
  selector: 'app-main-panel',
  templateUrl: './main-panel.component.html',
  styleUrls: ['./main-panel.component.css']
})
export class MainPanelComponent implements OnInit {

  public bootstrap: { ip: string; port: number; };

  public nodes = new Array<Node>();

  public errorMessage$: Observable<Error>;

  public inQuorum$: Observable<boolean>;

  private prevNodes: Node[] = [];

  public columns = 5;


  constructor(
    private store: Store<AppState>,
    private mediaObserver: MediaObserver
    
  ) { }

  ngOnInit() {

    this.mediaObserver.media$.subscribe((change: MediaChange) => {
      if(change.mqAlias == 'lg') this.columns = 5
      else if(change.mqAlias == 'md') this.columns = 4
      else if(change.mqAlias == 'sm') this.columns = 2
      else if(change.mqAlias == 'xs') this.columns = 1
    })

    this.store.select(s => s.system.bootstrap)
      .pipe(filter(b => b != null))
      .subscribe(b => this.bootstrap = b )

    this.store.select(s => s.nodes.nodes)
      .pipe(
        filter(nodes => nodes != null && nodes.length > this.prevNodes.length)
      ).subscribe(nodes => { this.prevNodes = this.nodes; this.nodes = nodes; })

    this.errorMessage$ = this.store.select(s => s.nodes.errorMessage)
  }
}
