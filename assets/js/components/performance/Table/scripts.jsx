import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow} from "@material-ui/core";

class TabularView extends Component {
    render() {
        const rows = [
            {'name': 'Frozen yoghurt', 'calories': 159, 'fat': 6.0, 'carbs': 24, 'protein': 4.0},
            {'name': 'Ice cream sandwich', 'calories': 159, 'fat': 6.0, 'carbs': 24, 'protein': 4.0},
            {'name': 'Eclair', 'calories': 159, 'fat': 6.0, 'carbs': 24, 'protein': 4.0},
            {'name': 'Cupcake', 'calories': 159, 'fat': 6.0, 'carbs': 24, 'protein': 4.0},
            {'name': 'Gingerbread', 'calories': 159, 'fat': 6.0, 'carbs': 24, 'protein': 4.0}
        ];

        return (
              <TableContainer component={Paper}>
                <Table sx={{minWidth: 650}} aria-label="simple table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Dessert (100g serving)</TableCell>
                            <TableCell align="right">Calories</TableCell>
                            <TableCell align="right">Fat&nbsp;(g)</TableCell>
                            <TableCell align="right">Carbs&nbsp;(g)</TableCell>
                            <TableCell align="right">Protein&nbsp;(g)</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rows.map((row) => (
                            <TableRow
                                key={row.name}
                                sx={{'&:last-child td, &:last-child th': {border: 0}}}
                            >
                                <TableCell component="th" scope="row">
                                    {row.name}
                                </TableCell>
                                <TableCell align="right">{row.calories}</TableCell>
                                <TableCell align="right">{row.fat}</TableCell>
                                <TableCell align="right">{row.carbs}</TableCell>
                                <TableCell align="right">{row.protein}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        );
    }
}

function scripts() {
    const parent = document.getElementById('js-initTabularView');

    ReactDOM.render(
        <TabularView
        />, parent
    )
}


export default scripts();