import { Component, OnInit } from '@angular/core';
import { Store } from '@ngrx/store';
import { AppState } from '../reducers';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {

  public config$: Observable<{ N: number; capacity: number; difficulty: number; }>;
  public bootstrap$: Observable<{ ip: string; port: number; }>;

  constructor(private store: Store<AppState>) { 
    
  }

  ngOnInit() {
    this.config$ = this.store.select(s => s.system.configuration)
    this.bootstrap$ = this.store.select(s => s.system.bootstrap)
  }

}
