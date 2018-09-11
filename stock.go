package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

const (
	Min = 0.00001

	ContentType = "application/json;charset=utf-8"

	FundomentalURL = "https://open.lixinger.com/api/a/stock/fundamental"
	IndustryURL    = "https://open.lixinger.com/api/a/stock/fs/industry"
)

type Lixinger struct {
	StockCodes []string `json:"stockCodes"`
	Date       string   `json:"date,omitempty"`
	StartDate  string   `json:"startDate,omitempty"`
	EndDate    string   `json:"endDate,omitempty"`
	Metrics    []string `json:"metrics"`
	Token      string   `json:"token"`
}

// 基本面信息，需要具体的日期
func (l *Lixinger) Fundamental(code string) {
	l.StockCodes = []string{code}
	l.Date = time.Now().Format("2006-01-02")
	l.Metrics = []string{
		"pb", "pb_pos10", "pb_pos_all",
		"pe_ttm", "pe_ttm_pos10", "pe_ttm_pos_all",
		"d_pe_ttm", "d_pe_ttm_pos10", "d_pe_ttm_pos_all",
	}
	body := l.Format()
	if body == nil {
		fmt.Println("POST数据格式化错误")
	}
	resp, err := http.Post(FundomentalURL, ContentType, body)
	defer resp.Body.Close()
	if err != nil {
		fmt.Println("理杏仁API出错：", err)
		os.Exit(1)
	}
	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("读取数据出错：", err)
		os.Exit(1)
	}
	var d FunResponseData
	if err := json.Unmarshal(content, &d); err != nil {
		fmt.Println("基本面数据格式化错误：", err)
		os.Exit(1)
	}
	validate := Analyze{FunData: d}
	validate.High()
}

// 经营信息，需要有开始及结束日期，只允许单个股票代码，不支持银行股
func (l *Lixinger) Industry(code, startDate string) {
	l.StockCodes = []string{code}
	l.StartDate = startDate
	l.EndDate = time.Now().Format("2006-01-02")
	l.Metrics = []string{
		"q.profitStatement.bi.t", "q.balanceSheet.ar.t",
		"q.balanceSheet.s.t", "q.balanceSheet.tca_tcl_r.t",
	}
	body := l.Format()
	if body == nil {
		fmt.Println("POST数据格式化错误")
	}
	resp, err := http.Post(IndustryURL, ContentType, body)
	defer resp.Body.Close()
	if err != nil {
		fmt.Println("理杏仁API出错：", err)
		os.Exit(1)
	}
	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("读取数据出错：", err)
		os.Exit(1)
	}
	var d IndResponseData
	if err := json.Unmarshal(content, &d); err != nil {
		fmt.Println("经营信息数据格式化出错：", err)
		os.Exit(1)
	}
	validate := Analyze{IndData: d}
	validate.Remove()
	validate.Three()
}

func (l *Lixinger) Format() *bytes.Buffer {
	b, err := json.Marshal(l)
	if err != nil {
		fmt.Println(err)
		return nil
	}
	return bytes.NewBuffer(b)
}

// 对股票进行分析验证
type Analyze struct {
	IndData IndResponseData
	FunData FunResponseData
}

// 不对银行股做分析
func (a *Analyze) Remove() {
	if a.IndData.Data[0].Industry.CnName == "银行" {
		fmt.Println("不支持银行股的筛选验证")
		os.Exit(0)
	}
}

func (a *Analyze) High() {
	for _, fd := range a.FunData.Data {
		if Smaller(0.50000, fd.Pb_pos10) {
			msg := fmt.Sprintf("当前PB: %f，PB分位点：%f，大于50%，估值过高，不合格", fd.Pb, fd.Pb_pos10)
			fmt.Println(msg)
			os.Exit(0)
		}
		if Smaller(0.50000, fd.Pe_ttm_pos10) {
			msg := fmt.Sprintf("当前PE: %f，PE分位点：%f，大于50%，估值过高，不合格", fd.Pe_ttm, fd.Pe_ttm_pos10)
			fmt.Println(msg)
			os.Exit(0)
		}
	}
}

func (a *Analyze) One() {

}

// 流动比率 < 1 应该予以剔除
func (a *Analyze) Three() {
	for _, fd := range a.IndData.Data {
		if strings.Split(fd.Date, "-")[1] == "12" {
			r := fd.Q.BalanceSheet.Tca_tcl_r.T
			if Smaller(r, 1.0000) {
				msg := fmt.Sprintf("%s年度的流动比率小于1，不符合白马股条件，不合格", strings.Split(fd.Date, "-")[0])
				fmt.Println(msg)
				os.Exit(0)
			}
		}
	}
	os.Exit(0)
}

func Smaller(a, b float64) bool {
	return math.Max(a, b) == b && math.Abs(a-b) > Min
}

func main() {
	help := flag.Bool("help", false, "获取帮助")
	token := flag.String("token", "5e9f7dc2-cc65-4e60-a8ba-47d13e401b7a", "理杏仁API token，可以从理杏仁网站获取")
	stockCode := flag.String("code", "000651", "股票代码")
	startYear := flag.String("year", "2014", "开始年份")
	flag.Parse()

	if *help {
		Usage()
		return
	}

	code, err := strconv.Atoi(*stockCode)
	if err != nil || code >= 999999 || code <= 0 {
		fmt.Println("股票代码错误")
		return
	}
	startDate := fmt.Sprintf("%s-01-01", *startYear)

	data := Lixinger{
		Token:   *token,
		Metrics: []string{"pb", "pb_pos10", "pb_pos_all"},
	}
	fmt.Println(startDate)
	data.Fundamental(*stockCode)
	// data.Industry(*stockCode, startDate)
}

type Total struct {
	T float64 `json:"t"`
}

type ProfitStatement struct {
	Bi Total `json:"bi"`
}

type BalanceSheet struct {
	Ar        Total `json:"ar"`
	S         Total `json:"s"`
	Tca_tcl_r Total `json:"tca_tcl_r"`
}

type Industry struct {
	CnName string `json:"cnName"`
}

type Q struct {
	ProfitStatement ProfitStatement `json:"profitStatement"`
	BalanceSheet    BalanceSheet    `json:"balanceSheet"`
}

type IndustryData struct {
	StockCode   string   `json:"stockCode"`
	StockCnName string   `json:"stockCnName"`
	Date        string   `json:"date"`
	Q           Q        `json:"q"`
	Industry    Industry `json:"industry"`
}

type FundamentalData struct {
	Date             string   `json:"date"`
	StockCode        string   `json:"stockCode"`
	StockCnName      string   `json:"stockCnName"`
	Pb               float64  `json:"pb"`
	Pb_pos10         float64  `json:"pb_pos10"`
	Pb_pos_all       float64  `json:"pb_pos_all"`
	Pe_ttm           float64  `json:"pe_ttm"`
	Pe_ttm_pos10     float64  `json:"pe_ttm_pos10"`
	Pe_ttm_pos_all   float64  `json:"pe_ttm_pos_all"`
	D_pe_ttm         float64  `json:"d_pe_ttm"`
	D_pe_ttm_pos10   float64  `json:"d_pe_ttm_pos10"`
	D_pe_ttm_pos_all float64  `json:"d_pe_ttm_pos_all"`
	Industry         Industry `json:"industry"`
}

type IndResponseData struct {
	Code int            `json:"code"`
	Msg  string         `json:"msg"`
	Data []IndustryData `json:"data"`
}

type FunResponseData struct {
	Code int               `json:"code"`
	Msg  string            `json:"msg"`
	Data []FundamentalData `json:"data"`
}

func Usage() {
	fmt.Println(`Usage:

choseStock [option]

  -help bool
        获取帮助
  -code string
    	股票代码 (default "000651")
  -token string
    	理杏仁API token，可以从理杏仁网站获取 (default "5e9f7dc2-cc65-4e60-a8ba-47d13e401b7a")
  -year string
    	开始年份 (default "2014")
	`)
}