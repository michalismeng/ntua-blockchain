import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NodeService } from 'src/services/node.service';
import { HttpClientModule } from '@angular/common/http';
import { LayoutComponent } from './layout/layout.component';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MaterialModule } from './material/material.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { SetupBootstrapComponent } from './setup-bootstrap/setup-bootstrap.component';
import { MainPanelComponent } from './main-panel/main-panel.component';
import { StoreModule } from '@ngrx/store';
import { reducers, metaReducers } from './reducers';
import { environment } from 'src/environments/environment';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';
import { EffectsModule } from '@ngrx/effects';
import { NodeEffect } from './effects/node.effects';
import { NodePanelComponent } from './node-panel/node-panel.component';
import { ConfigService } from 'src/services/config.service';
import { TransactionComponent } from './transaction/transaction.component';
import { SystemEffect } from './effects/system.effects';


@NgModule({
  declarations: [
    AppComponent,
    LayoutComponent,
    HeaderComponent,
    FooterComponent,
    SetupBootstrapComponent,
    MainPanelComponent,
    NodePanelComponent,
    TransactionComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FlexLayoutModule,
    AppRoutingModule,
    MaterialModule,
    FormsModule,
    ReactiveFormsModule,

    StoreModule.forRoot(reducers, { metaReducers }), !environment.production ? StoreDevtoolsModule.instrument() : [],
    EffectsModule.forRoot([NodeEffect, SystemEffect]),
  ],
  providers: [NodeService, ConfigService],
  bootstrap: [AppComponent]
})
export class AppModule { }
