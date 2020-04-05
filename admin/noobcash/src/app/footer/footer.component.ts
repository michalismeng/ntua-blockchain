import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { AppState } from '../reducers';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent implements OnInit {

  public systemOrdinal: number;
  public noNodes: number;

  constructor(private store: Store<AppState>) { }

  ngOnInit() {
    this.store.select(s => s.system.systemOrdinal).subscribe(o => this.systemOrdinal = o)
    this.store.select(s => s.nodes.nodes).subscribe(ns => this.noNodes = ns.length)
  }

}
