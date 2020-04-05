import { Component, OnInit } from '@angular/core';
import { AppState } from '../reducers';
import { Store } from '@ngrx/store';
import { NodeService } from 'src/services/node.service';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { KillSystem } from '../actions/system.actions';

@Component({
  selector: 'app-transaction',
  templateUrl: './transaction.component.html',
  styleUrls: ['./transaction.component.css']
})
export class TransactionComponent implements OnInit {

  public form: FormGroup;

  constructor(
    private store: Store<AppState>,
    private nodeService: NodeService,
    private fb: FormBuilder
  ) { 
    this.form = this.fb.group({
      sourceNode: ['', Validators.required],
      targetNode: ['', Validators.required],
      amount: ['', Validators.required]
    })
  }

  ngOnInit() {
  }


  submit() {
    let value = this.form.value;

    this.store.select(s => s.nodes.nodes)
      .subscribe(ns => this.nodeService.doTransaction(value.sourceNode, value.targetNode, value.amount, ns).subscribe())
      .unsubscribe()
  }

  killall() {
    this.store.dispatch(new KillSystem())
  }

}
