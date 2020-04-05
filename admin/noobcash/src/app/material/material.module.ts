import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSidenavModule, MatToolbarModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, MatProgressBarModule, 
  MatCardModule, MatDividerModule, MatTooltipModule, MatFormFieldModule, MatInputModule, MatBadgeModule, MatGridListModule } from '@angular/material';


// -- Add extra material modules here
const materialModules = [
  MatSidenavModule,
  MatToolbarModule,
  MatButtonModule, 
  MatIconModule,
  MatProgressSpinnerModule,
  MatCardModule,
  MatProgressBarModule,
  MatDividerModule,
  
  MatTooltipModule,

  MatFormFieldModule,
  MatInputModule,
  
  MatBadgeModule,
  MatGridListModule
]


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    materialModules,
  ],
  exports:[
    materialModules,
  ],
  providers: [
  ]
})
export class MaterialModule { }
